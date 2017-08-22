from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from about.views import *

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {"template": "about/about.html"}, name="about"),
    
    url(r'^terms/$', direct_to_template, {"template": "about/terms.html"}, name="terms"),
    url(r'^privacy/$', direct_to_template, {"template": "about/privacy.html"}, name="privacy"),
    url(r'^dmca/$', direct_to_template, {"template": "about/dmca.html"}, name="dmca"),
    url(r'^what_next/$', what_next, name="what_next"),
    url(r'^rules/$', direct_to_template, {"template": "about/about_rules.html"}, name="about_rules"),
    url(r'^what_and_who/$', direct_to_template, {"template": "about/what_and_who.html"}, name="what_and_who"),
)
