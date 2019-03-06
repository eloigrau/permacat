from django import forms
from .models import Article, Commentaire
from django.utils.text import slugify
import itertools
from django.utils.timezone import now
from django.utils.formats import localize


class ArticleForm(forms.ModelForm):
    contenu = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}))

    class Meta:
        model = Article
        fields = ['categorie', 'titre', 'contenu']

    def save(self, userProfile):
        instance = super(ArticleForm, self).save(commit=False)

        max_length = Article._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Article.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.date = localize(now, use_l10n=True)
        instance.auteur = userProfile

        instance.save()

        return instance


class ArticleChangeForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu', ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        exclude = ['article','auteur_comm']
