from django.contrib.sites.models import Site
from django.conf import settings
from facebook.models import *
import urllib, cgi, simplejson

class FacebookBackend:
	def authenticate(self, token=None, request=None):
		args = dict(client_id=settings.APP_ID, redirect_uri="http://" + Site.objects.get(id=settings.SITE_ID).domain + '/facebook/authenticate/')
		args["client_secret"] = settings.APP_SECRET
		args["code"] = token
		response = cgi.parse_qs(urllib.urlopen(
		"https://graph.facebook.com/oauth/access_token?" +
			urllib.urlencode(args)).read())
		access_token = response["access_token"][-1]
		me_json = urllib.urlopen("https://graph.facebook.com/me?" + urllib.urlencode(dict(access_token=access_token)))
		profile = simplejson.load(me_json)
		try:
			fb_user = FacebookUser.objects.get(facebook_id = str(profile["id"]))
		except FacebookUser.DoesNotExist:
			if request.user.is_authenticated():
				# User connects with Facebook while logged in
				fb_user = FacebookUser(user = request.user, 
					facebook_id = profile['id'],
					access_token = access_token,
					token_valid = True)
				fb_user.save()
			request.session['fb_id'] = profile['id']
			request.session['fb_token'] = access_token
			# return None no matter whether the current user is logged in
			return None
		fb_user.access_token = access_token
		fb_user.save()
		return fb_user.user
	
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
