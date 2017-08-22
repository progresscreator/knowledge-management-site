from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from iquest.views import *

urlpatterns = patterns('',
    url(r'^$', iquest_home, name="iquest_home"),
    url(r'^ask/$', iquest_ask, name="iquest_ask"),
    url(r'^requests/$', iquest_requests, name="iquest_requests"),
    url(r'^request/(?P<request_id>\d+)/$', iquest_request, name="iquest_request"),
    url(r'^response/(?P<request_id>\d+)/$', iquest_response, name="iquest_response"),
)

