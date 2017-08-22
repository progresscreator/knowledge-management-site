from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from egghead.views import *

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "egghead/egghead.html"}, name="egghead"),
	url(r'^profile/(?P<username>[\w\._-]+)/$', egghead_detail, name="egghead_detail"),
	url(r'^edit/$', egghead_edit, name="egghead_edit"),
    url(r'^ajax/tribe/members/(?P<tribe_id>\d+)/$', egghead_ajax_tribe_members, name="egghead_ajax_tribe_members"),
	url(r'^facebook_no_user_error/$', direct_to_template, {"template": "egghead/egghead_facebook_no_user.html"}, name="facebook_no_user_error"),
)
