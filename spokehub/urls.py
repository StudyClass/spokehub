from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from spokehub.main import views
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

urlpatterns = patterns(
    '',
    (r'^accounts/', include('userena.urls')),
    (r'^$', views.IndexView.as_view()),

    (r'^news/$', views.NewsIndexView.as_view()),
    (r'^news/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
     views.ItemDetailView.as_view()),
    (r'^news/add/$', views.NewsCreateView.as_view()),

    (r'^about/$', TemplateView.as_view(template_name="about.html")),

    (r'^challenge/$', views.ChallengeIndexView.as_view()),
    (r'^challenge/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
     views.ItemDetailView.as_view()),
    (r'^challenge/add/$', views.ChallengeCreateView.as_view()),

    (r'^case/$', views.CaseIndexView.as_view()),
    (r'^case/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
     views.ItemDetailView.as_view()),
    (r'^case/add/$', views.CaseCreateView.as_view()),

    (r'network/$', TemplateView.as_view(template_name='network/index.html')),

    (r'contact/$', TemplateView.as_view(template_name='contact/index.html')),

    (r'item/(?P<pk>\d+)/reply/$', views.ReplyToItemView.as_view()),
    (r'test/$', TemplateView.as_view(template_name='layout_test.html')),

    (r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),
)
