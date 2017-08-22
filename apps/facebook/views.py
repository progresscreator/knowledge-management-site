from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import login, logout, authenticate
from facebook.models import *
import urllib, cgi, simplejson
import logging

flogger = logging.getLogger("pwe.facebook")

def authenticate_view(request):
	code = request.GET.get("code",None)
	if code:
		user = authenticate(token=code, request=request)
		if user != None:
			login(request, user)
			return HttpResponseRedirect(reverse("egghead_detail", 
					kwargs={"username": request.user.username}))
		else:
			if request.user.is_authenticated():
				return HttpResponseRedirect(reverse("egghead_detail", 
						kwargs={"username": request.user.username}))
			else:
				return HttpResponseRedirect(reverse("facebook_no_user_error"))
	else:
		args = dict(client_id=settings.APP_ID, redirect_uri="http://" + Site.objects.get(id=settings.SITE_ID).domain + '/facebook/authenticate/', scope="user_status, email, publish_stream, offline_access")
		flogger.debug(str(args))
		return HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))

def associate_view(request):
	args = dict(client_id=settings.APP_ID, redirect_uri="http://" + Site.objects.get(id=settings.SITE_ID).domain + '/facebook/authenticate/', scope="user_status, email, publish_stream, offline_access")
	return HttpResponseRedirect("https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args))

def register(request):
	if request.method == "POST":
		user = User.objects.create_user(request.POST["username"], request.POST["email"])
		fb_user = FacebookUser(user = user, facebook_id = request.session['fb_id'])
		fb_user.save()
		return HttpResponseRedirect('/authenticate/')
	else:
		return render_to_response("anonymous/register.html")
	
def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')
