import random
from django import template

from ..models import Album
from ..models import Photo

register = template.Library()


@register.inclusion_tag('photologue/tags/next_in_album.html')
def next_in_album(photo, album):
    return {'photo': photo.get_next_in_album(album)}


@register.inclusion_tag('photologue/tags/prev_in_album.html')
def previous_in_album(photo, album):
    return {'photo': photo.get_previous_in_album(album)}


@register.simple_tag
def cycle_lite_album(album_title, height, width):
    """Generate image tags for jquery slideshow album.
    See http://malsup.com/jquery/cycle/lite/"""
    html = ""
    first = 'class="first"'
    for p in Album.objects.get(title=album_title).public():
        html += u'<img src="%s" alt="%s" height="%s" width="%s" %s />' % (
            p.get_display_url(), p.title, height, width, first)
        first = None
    return html


@register.tag
def get_photo(parser, token):
    """Get a single photo from the photologue library and return the img tag to display it.

    Takes 3 args:
    - the photo to display. This can be either the slug of a photo, or a variable that holds either a photo instance or
      a integer (photo id)
    - the photosize to use.
    - a CSS class to apply to the img tag.
    """
    try:
        # Split the contents of the tag, i.e. tag name + argument.
        tag_name, photo, photosize, css_class = token.split_contents()
    except ValueError:
        msg = '%r tag requires 3 arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    return PhotoNode(photo, photosize[1:-1], css_class[1:-1])


class PhotoNode(template.Node):

    def __init__(self, photo, photosize, css_class):
        self.photo = photo
        self.photosize = photosize
        self.css_class = css_class

    def render(self, context):
        try:
            a = template.Variable(self.photo).resolve(context)
        except:
            a = self.photo
        if isinstance(a, Photo):
            p = a
        else:
            try:
                p = Photo.objects.get(slug=a)
            except Photo.DoesNotExist:
                # Ooops. Fail silently
                return None
        if not p.is_public:
            return None
        func = getattr(p, 'get_%s_url' % (self.photosize), None)
        if func is None:
            return 'A "%s" photo size has not been defined.' % (self.photosize)
        else:
            return u'<img class="%s" src="%s" alt="%s" />' % (self.css_class, func(), p.title)


@register.tag
def get_rotating_photo(parser, token):
    """Pick at random a photo from a given photologue album and return the img tag to display it.

    Takes 3 args:
    - the album to pick a photo from. This can be either the slug of a album, or a variable that holds either a
      album instance or a album slug.
    - the photosize to use.
    - a CSS class to apply to the img tag.
    """
    try:
        # Split the contents of the tag, i.e. tag name + argument.
        tag_name, album, photosize, css_class = token.split_contents()
    except ValueError:
        msg = '%r tag requires 3 arguments' % token.contents[0]
        raise template.TemplateSyntaxError(msg)
    return PhotoAlbumNode(album, photosize[1:-1], css_class[1:-1])


class PhotoAlbumNode(template.Node):

    def __init__(self, album, photosize, css_class):
        self.album = album
        self.photosize = photosize
        self.css_class = css_class

    def render(self, context):
        try:
            a = template.resolve_variable(self.album, context)
        except:
            a = self.album
        if isinstance(a, Album):
            g = a
        else:
            try:
                g = Album.objects.get(slug=a)
            except Album.DoesNotExist:
                return None
        photos = g.public()
        if len(photos) > 1:
            r = random.randint(0, len(photos) - 1)
            p = photos[r]
        elif len(photos) == 1:
            p = photos[0]
        else:
            return None
        func = getattr(p, 'get_%s_url' % (self.photosize), None)
        if func is None:
            return 'A "%s" photo size has not been defined.' % (self.photosize)
        else:
            return u'<img class="%s" src="%s" alt="%s" />' % (self.css_class, func(), p.title)
