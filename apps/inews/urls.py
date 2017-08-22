from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.create_update import create_object
from django.views.generic.list_detail import object_detail, object_list
from inews.views import *
from django.contrib.auth.decorators import login_required
from inews.forms import AnnouncePostForm
from inews.models import AnnouncePost
import datetime

info_dict = { 'queryset' : AnnouncePost.objects.all().order_by('-thumbs') }

urlpatterns = patterns('',
	# show main-page announceposts
	url(r'^$', inews_home, name="inews_home"),

	# show all announceposts
	url(r'^articles/$', inews_articles, name="inews_articles"),

	# create an announcepost
    url(r'^submit/$', create_announcepost, name="inews_submit"),

	# detail about an announcepost
	url(r'^post/(?P<announcepost_id>\d+)/$', inews_announcepost, name="inews_announcepost"),
	url(r'^thumbs/$', inews_thumb_check, name="inews_thumb_check"),
	url(r'^thumb/up/(?P<announcepost_id>\d+)/$', inews_thumbup, name="inews_thumbup"),
	url(r'^thumb/down/(?P<announcepost_id>\d+)/$', inews_thumbdown, name="inews_thumbdown"),

    # tipping
    url(r'^post/tipping/$', inews_tipping, name="inews_tipping"),

	# inews help
	url(r'^help/$', inews_help, name="inews_help"),

	# inews tags
	url(r'^tag/(?P<tag_id>\d+)/$', inews_tag, name="inews_tag"),

	# ajax calls
	url(r'^ajax/articles/(?P<qtype>\w+)/$', inews_ajax_articles, name="inews_ajax_articles"),
	url(r'^ajax/articles/tags/(?P<qtype>\w+)/(?P<tag_id>\d+)/$', inews_ajax_articles, name="inews_ajax_tag_articles"),

	# main-page sort
	url(r'^(?P<qtype>\w+)/$', inews_home, name="inews_home"),
)

