from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from core.views import *

urlpatterns = patterns('',
    url(r'^settings/$', barter_settings, name="barter_settings"),
	url(r'^features/add/$', feature_add, name="feature_add"),
	url(r'^experts/tag/(?P<tag_id>\d+)/$', core_tag_experts, name="core_tag_experts"),
	url(r'^experts/tag_news/(?P<tag_id>\d+)/$', core_tag_experts_news, name="core_tag_experts_news"),
	#url(r'^features/edit/(?P<feature_id>\d+/$', feature_edit, name="feature_edit"),
)

urlpatterns += patterns('',
    url(r'^json/tags/$', barter_json_tags, name="barter_json_tags"),
    url(r'^json/users/$', barter_json_users, name="barter_json_users"),
)
