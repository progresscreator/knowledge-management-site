from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import *
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat

class FacebookUser(models.Model):
	user = models.OneToOneField(User)
	facebook_id = models.CharField(max_length=150,unique=True, blank=True)
	access_token = models.CharField(max_length=150,blank=True)
	token_valid	= models.BooleanField(default=False)

	def __unicode__(self):
		return self.user.egghead.display_name()
