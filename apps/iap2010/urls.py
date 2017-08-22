from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from iap2010.views import *

urlpatterns = patterns('',
    url(r'^$', iap2010_home, name="iap2010_home"),
)
