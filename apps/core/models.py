from django.db import models
from django.db.models import Sum, Avg
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime, timedelta
import math
import logging

class ICoreCategory(models.Model):
	name				= models.CharField(max_length=32)
	parent				= models.ForeignKey("self")

	def __unicode__(self):
		return self.name

# Create your models here.
class MasterPiece(models.Model):
	SHARING_OPTIONS = (
		("P", _("Public")),
		("F", _("Friends")),
		("G", _("Groups")),
		("B", _("Both friends and selected groups")),
		("U", _("Targeted Users")),
	)
	MP_CODES = (
		("DO", _("Document")),
		("DR", _("Document Request")),
		("QA", _("Question Amendment")),
		("QC", _("Question Comment")),
		("AC", _("Answer Comment")),
		("ID", _("Idea")),
		("DC", _("Idea Comment")),
	)
	creator				= models.ForeignKey(User, related_name="masterpieces_produced")
	time_stamp			= models.DateTimeField()

	mp_code				= models.CharField(max_length=2, choices=MP_CODES, blank=True,null=True)
	title				= models.CharField(max_length=256, blank=True)
	details				= models.TextField(blank=True)
	anonymous			= models.BooleanField(default=False, help_text=_("Share anonymously?"))

	points_offered		= models.IntegerField(default=0)
	points_final		= models.IntegerField(default=0)
	points_expiration	= models.DateTimeField(blank=True, null=True)

	tags				= models.CharField(max_length=512, blank=True)
	categories			= models.ManyToManyField(ICoreCategory, blank=True, null=True)

	sharing				= models.CharField(max_length=1, choices=SHARING_OPTIONS, default="P")

	thumb_up			= models.IntegerField(default=0)
	thumb_down			= models.IntegerField(default=0)
	thumbs				= models.IntegerField(default=0, blank=True, null=True)

	to_users			= models.ManyToManyField(User, blank=True, null=True, 
							related_name="masterpieces_shared")
	to_groups			= models.ManyToManyField("tribes.Tribe", blank=True, null=True)

	visits				= models.IntegerField(default=0)
	deleted				= models.BooleanField(default=False)
	# "status" and "type" need to be defined in subclasses

	def __unicode__(self):
		return self.title

	def update_thumbs(self):
		thumbs = self.thumb_up - self.thumb_down
		self.thumbs = thumbs
		self.save()

	def update_visits(self):
		self.visits += 1
		self.save()
	
	def display_name(self):
		if self.anonymous:
			return ugettext("An Egghead")
		else:
			if self.creator.get_full_name():
				return self.creator.get_full_name()
			else:
				return self.creator.username

	def time_string_l(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

class IThumb(models.Model):
	UP_DOWN_CHOICES = (
		("U", _("Thumb up")),
		("D", _("Thumb down")),
	)
	thumber				= models.ForeignKey(User)
	up_or_down			= models.CharField(max_length=1, choices=UP_DOWN_CHOICES)
	time_stamp			= models.DateTimeField()
	
	def __unicode__(self):
		if self.up_or_down == "U":
			return _("%(thumber_name)s thumbs up") % {"thumber_name": self.thumber.egghead.display_name()}
		else:
			return _("%(thumber_name)s thumbs down") % {"thumber_name": self.thumber.egghead.display_name()}
	def date_string(self):
		return self.time_stamp.strftime("%Y-%m-%d")
		
	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def display_name(self):
		return self.thumber.egghead.display_name()

class IDonate(models.Model):
	donater				= models.ForeignKey(User)
	amount				= models.IntegerField(default=0)
	time_stamp			= models.DateTimeField()

	def __unicode__(self):
		return _("%(donater_name)s donates %(amount)d points") % {
				"donater_name": self.donater.egghead.display_name(),
				"amount": self.amount
			}

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def display_name(self):
		return self.donater.egghead.display_name()

class IComment(MasterPiece):
	parent				= models.ForeignKey("self", blank=True, null=True)
	layer				= models.IntegerField(default=1)

class Settings(models.Model):
	user						= models.OneToOneField(User)	
	mobile						= models.CharField(max_length=12, blank=True)
	new_q_notification_txt		= models.BooleanField(default=False)
	new_q_notification_email	= models.BooleanField(default=False)
	new_feature_email			= models.BooleanField(default=False)

	def __unicode__(self):
		return _("%(user_name)s's settings") % {
				"username": self.user.egghead.display_name()
			}

class Feature(models.Model):
	TYPE_CHOICES = (
		("B", _("Bug fixes")),
		("F", _("New features")),
	)
	committer			= models.ForeignKey(User)
	title				= models.CharField(max_length=128)
	type				= models.CharField(max_length=1, choices=TYPE_CHOICES)
	description			= models.TextField(blank=True)
	creation_date		= models.DateField()

	def __unicode__(self):
		return self.title

