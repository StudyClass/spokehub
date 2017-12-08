import os.path
import userena.views
import django.contrib.auth.views
import django.views.static

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import TemplateView
from spokehub.main import views
from spokehub.main.forms import CustomAuthenticationForm
from spokehub.profile.forms import ExtendedEditProfileForm
from spokehub.profile.views import ProfileListView
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

urlpatterns = [
    url(r'^accounts/logout/$',
        django.contrib.auth.views.logout,
        {'next_page': '/'},
        name='auth_logout'),
    url(r'^accounts/signin/$',
        userena.views.signin,
        {'auth_form': CustomAuthenticationForm},
        name='userena_signin'),
    url(r'^accounts/(?P<username>[\@\.\w-]+)/edit/$',
        userena.views.profile_edit,
        {'edit_profile_form': ExtendedEditProfileForm},
        name='userena_profile_edit'),
    url(r'^accounts/$',
        login_required(ProfileListView.as_view(paginate_by=100)),
        name='userena_profile_list'),
    url(r'^accounts/', include('userena.urls')),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"),
        name='about'),
    url(r'^network/$', views.IndexView.as_view(
        template_name='network/index.html')),
    url(r'^how/$', views.IndexView.as_view(
        template_name='how/index.html'), name='how'),

    url(r'^we/$', views.ConversationIndexView.as_view(
        template_name='we/index.html'), name='we'),
    url(r'^we/archive/$', views.ConversationIndexView.as_view(
        paginate_by=10, template_name='we/archive.html'),
        name='we-archive'),
    url(r'^we/question/(?P<year>\d+)/'
        '(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
        views.ConversationDetailView.as_view(
            template_name='we/question.html'), name='question'),
    url(r'^we/question/(?P<year>\d+)/(?P<month>\d+)/'
        r'(?P<day>\d+)/(?P<pk>\d+)/edit/$',
        views.ConversationUpdateView.as_view(), name='edit-question'),
    url(r'^we/question/(?P<year>\d+)/(?P<month>\d+)/'
        r'(?P<day>\d+)/(?P<pk>\d+)/delete/$',
        views.ConversationDeleteView.as_view(), name='delete-question'),
    url(r'^we/ask/$', views.ConversationCreateView.as_view(
        template_name='we/ask.html'), name='ask-question'),
    url(r'^reply/(?P<pk>\d+)/edit/$',
        views.ReplyUpdateView.as_view(), name='edit-reply'),
    url(r'^reply/(?P<pk>\d+)/delete/$',
        views.ReplyDeleteView.as_view(), name='delete-reply'),
    url(r'^reply/(?P<pk>\d+)/add_comment/$',
        views.AddCommentView.as_view(), name='add-comment'),

    url(r'^work/', include('spokehub.work.urls')),

    url(r'^now/$', views.IndexView.as_view(
        template_name='now/index.html'), name='now'),
    url(r'^weold/$', views.IndexView.as_view(
        template_name='main/we.html')),
    url(r'^convo/$', views.IndexView.as_view(
        template_name='main/conversation.html')),
    url(r'^404-test/$', views.IndexView.as_view(
        template_name='404.html')),
    url(r'^user_index/$', views.TemplateView.as_view(
        template_name='userena/user_index.html')),
    url(r'^privacy/$', views.TemplateView.as_view(
        template_name='main/privacy.html')),

    url(r'^scroll/$', views.TemplateView.as_view(
        template_name='infinite-scroll-master/test/index.html'),
        name='scroll'),

    url(r'^conversation/(?P<pk>\d+)/reply/$',
        views.ReplyToConversationView.as_view(),
        name='reply-to-question'),

    url(r'^test/$', TemplateView.as_view(template_name='layout_test.html')),

    url(r'^edit/', include('spokehub.edit.urls')),
    url(r'^invite/', include('spokehub.invite.urls')),
    url(r'^contact/', include('spokehub.contact.urls')),
    url(r'^broadcast/', include('spokehub.broadcast.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html"),
        name='stats'),
    url(r'^smoketest/', include('smoketest.urls')),
    url(r'^uploads/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT}),
]
