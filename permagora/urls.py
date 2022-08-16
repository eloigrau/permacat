"""permagora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.urls import path
from permagora import views
from django.views.generic import TemplateView
#from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

# On import les vues de Django, avec un nom spécifique
from django.contrib.auth.decorators import login_required

# admin.autodiscover()
from django.contrib import admin

app_name = 'permagora'

urlpatterns = [
    path('gestion/', admin.site.urls),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^$', views.bienvenue, name='bienvenue'),
    url(r'^planSite/$', views.planSite, name='planSite'),
    url(r'^risques/$', views.risques, name='risques'),
    url(r'^introduction/$', views.introduction, name='introduction'),
    url(r'^preambule/$', views.preambule, name='preambule'),
    url(r'^preconisations/$', views.preconisations, name='preconisations'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^contact/$', views.contact, name='contact', ),
    url(r'^signer/$', views.signer, name='signer', ),
    url(r'^designer/$', views.designer, name='designer', ),
    url(r'^statistiques/$', views.statistiques, name='statistiques', ),
    url(r'^signataires/$', views.signataires, name='signataires', ),

    url(r'^accounts/profil/(?P<user_id>[0-9]+)/$', login_required(views.profil), name='profil', ),
    url(r'^accounts/profil/(?P<user_username>[-\w.]+)/$', login_required(views.profil_nom), name='profil_nom', ),
    url(r'^accounts/profile/$', login_required(views.profil_courant), name='profil_courant', ),

    url(r'^merci/$', views.merci, name='merci'),
    path('auth/', include('django.contrib.auth.urls')),
    url(r'^propositions/$', views.propositions, name='propositions', ),
    url(r'^organisationPermagora/$', views.organisationPermagora, name='organisationPermagora', ),
    url(r'^presentationPermagora/$', views.presentationPermagora, name='presentationPermagora', ),
    url(r'^cgu/$', views.cgu, name='cgu', ),
    url(r'^liens/$', views.liens, name='liens', ),
    url(r'^fairedon/$', views.fairedon, name='fairedon', ),
    url(r'^contact_admins/$', views.contact_admins, name='contact_admins',),

    url(r'^ajouterPoleCharte/$', views.ajouterPoleCharte, name='ajouterPoleCharte', ),
    url(r'^voirProposition/(?P<slug>[-\w]+)$', views.voirProposition, name='voirProposition', ),
    url(r'^ajouterVote_plus/(?P<slug>[-\w]+)$', views.ajouterVote_plus, name='ajouterVote_plus', ),
    url(r'^ajouterVote_moins/(?P<slug>[-\w]+)$', views.ajouterVote_moins, name='ajouterVote_moins', ),
    path(r'ajouterProposition/', views.ajouterProposition, name='ajouterProposition'),
    path(r'voirNotifications/', views.voirNotifications, name='voirNotifications'),

    url(r'^modifierProposition/(?P<slug>[-\w]+)$',
        login_required(views.ModifierProposition.as_view(), login_url='/auth/login/'), name='modifierProposition'),
    ]
urlpatterns += [
    url(r'^robots\.txt$', TemplateView.as_view(template_name="permagora/robots.txt", content_type='text/plain')),
]

from django.conf import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'permagora.views.handler404'
handler500 = 'permagora.views.handler500'
handler400 = 'permagora.views.handler400'
handler403 = 'permagora.views.handler403'
