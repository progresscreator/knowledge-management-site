from django.conf.urls.defaults import *
from facebook.views import authenticate_view,logout_view,register, associate_view

urlpatterns = patterns('',
    url(r'^authenticate/?$', view=authenticate_view,name='facebook_authenticate'),
    url(r'^associate/?$', view=associate_view,name='facebook_associate'),
    url(r'^logout/?$', view=logout_view,name='facebook_logout'),
    url(r'^register/?$', view=register,name='facebook_register'),
)
