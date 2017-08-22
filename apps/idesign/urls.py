from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from idesign.views import *

urlpatterns = patterns('',
    url(r'^$', idesign_home, name="idesign_home"),
    url(r'^submit/$', idesign_submit, name="idesign_submit"),
    url(r'^designidea/(?P<designidea_id>\d+)/$', idesign_designidea, name="idesign_designidea"),
    url(r'^designideas/$', idesign_designideas, name="idesign_designideas"),
    url(r'^post/thumbs/$', idesign_post_thumbs, name="idesign_post_thumbs"),
    url(r'^post/donate/$', idesign_post_donate, name="idesign_post_donate"),
)
