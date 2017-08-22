from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime, timedelta
import math
from core.models import ICoreCategory, MasterPiece

# Create your models here.

#class Document(models.Model):
#	SHARING_OPTIONS = (
#		("P", "Public"),
#		("F", "Friends"),
#		("G", "Groups"),
#		("B", "Both friends and selected groups"),
#		("U", "Targeted Users"),
#	)
#	owner				= models.ForeignKey(User, related_name="documents_owned")
#	creation_time		= models.DateTimeField()
#	edit_time			= models.DateTimeField(blank=True, null=True)
#
#	title				= models.CharField(max_length=128)
#	description			= models.TextField(blank=True)
#	anonymous			= models.BooleanField(default=False, help_text="Check if you want to stay anonymous")
#
#	tags				= models.CharField(max_length=512, blank=True)
#	categories			= models.ManyToManyField(ICoreCategory, blank=True, null=True)
#
#	sharing				= models.CharField(max_length=1, choices=SHARING_OPTIONS, default="P")
#
#	thumb_up			= models.IntegerField(default=0)
#	thumb_down			= models.IntegerField(default=0)
#	thumbs				= models.IntegerField(default=0, blank=True, null=True)
#	to_users			= models.ManyToManyField(User, related_name="documents_received",
#							blank=True, null=True)
#	to_groups			= models.ManyToManyField("tribes.Tribe", blank=True, null=True)
#	visits				= models.IntegerField(default=0)
#	downloads			= models.IntegerField(default=0)
#	deleted				= models.BooleanField(default=False)
#
#	doctype				= models.CharField(max_length=6, blank=True)
#	file				= models.FileField(upload_to="idoc/files/%Y/%m/%d/", null=True)
#
#	def __unicode__(self):
#		return self.title
#
#	def get_absolute_url(self):
#		from django.core.urlresolvers import reverse
#		return reverse("idoc_doc", kwargs={"doc_id": self.id})
#	
#	def creation_time_string_s(self):
#		return self.creation_time.strftime("%m-%d %I:%M%p")
#
#	def creation_time_string_l(self):
#		return self.creation_time.strftime("%Y-%m-%d,%I:%M%p")
#
#	def edit_time_string_s(self):
#		return self.edit_time.strftime("%m-%d %I:%M%p")
#
#	def edit_time_string_l(self):
#		return self.edit_time.strftime("%Y-%m-%d,%I:%M%p")
#	
#	def rating(self):
#		from django.db.models import Avg
#		if not DocumentRating.objects.filter(document=self):
#			return "N/A"
#		return DocumentRating.objects.filter(document=self).aggregate(Avg("rating"))["rating__avg"]
#
#	def rating_float(self):
#		from django.db.models import Avg
#		if not DocumentRating.objects.filter(document=self):
#			return 0
#		return DocumentRating.objects.filter(document=self).aggregate(Avg("rating"))["rating__avg"]
#
#		
#	def display_name(self):
#		if self.anonymous:
#			return "An Egghead"
#		else:
#			if self.owner.get_full_name():
#				return self.owner.get_full_name()
#			else:
#				return self.owner.username
#	
#	def update_thumbs(self):
#		thumbs = self.thumb_up - self.thumb_down
#		self.thumbs = thumbs
#		self.save()
#	
#	def update_visits(self):
#		self.visits = self.visits + 1
#		self.save()
#	def update_downloads(self):
#		self.downloads = self.downloads + 1
#		self.save()
#	
#
#class DownloadHistory(models.Model):
#	downloader			= models.ForeignKey(User)
#	document			= models.ForeignKey(Document)
#	time_stamp			= models.DateTimeField()
#
#	def __unicode__(self):
#		if self.downloader.get_full_name():
#			name = self.downloader.get_full_name()
#		else:
#			name = self.downloader.username
#		astr = name + " downloaded " + self.document.title + " at " +\
#				self.time_string_l()
#		return astr
#
#	def time_string_l(self):
#		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")
#
#class DocumentRating(models.Model):
#	rater				= models.ForeignKey(User)
#	rating              = models.IntegerField()
#	document			= models.ForeignKey(Document)
#	time_stamp			= models.DateTimeField()
#
#	def __unicode__(self):
#		if self.rater.get_full_name():
#			name = self.rater.get_full_name()
#		else:
#			name = self.rater.username
#		astr = name + " gave " + self.document.title + " a rating of " +\
#				str(self.rating) + self.time_string_l()
#		return astr
#
#	def time_string_l(self):
#		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")
#	def time_string_date(self):
#		return self.time_stamp.strftime("%Y %m-%d")

###############################################################################################
# New model design for idoc below
class IDocRequest(MasterPiece):

	def __unicode__(self):
		return _("Requesting document: %(doc_title)s") % {"doc_title": self.title}

class IDocument(MasterPiece):
	# A field for migration
	# olddoc				= models.ForeignKey(Document, blank=True, null=True)

	doctype				= models.CharField(max_length=20, blank=True)
	url					= models.URLField(blank=True, null=True)
	file				= models.FileField(upload_to="idoc/files/%Y/%m/%d/", blank=True,null=True)
	version				= models.CharField(max_length=10, blank=True)
	points_needed		= models.IntegerField(default=0)
	downloads			= models.IntegerField(default=0)
	freedownloads		= models.IntegerField(default=0)
	rating				= models.FloatField(default=0)
	docrequest			= models.ForeignKey(IDocRequest, blank=True, null=True)

	def get_absolute_url(self):
		from django.core.urlresolvers import reverse
		return reverse("idoc_doc", kwargs={"doc_id": self.id})

	def rating_string(self):
		if not self.idocrating_set.all():
			return "N/A"
		return "%.1f" % self.rating

	def update_rating(self):
		if not self.idocrating_set.all():
			self.rating = 0
		else: 
			from django.db.models import Avg
			self.rating = self.idocrating_set.aggregate(Avg("rating"))["rating__avg"]
		self.save()
	
	def update_downloads(self):
		self.downloads += 1
		if not self.points_needed:
			self.freedownloads += 1
		self.save()

class IDocDownload(models.Model):
	downloader			= models.ForeignKey(User)
	document			= models.ForeignKey(IDocument)
	time_stamp			= models.DateTimeField()
	fee					= models.IntegerField(default=0)

	def __unicode__(self):
		return _("%(downloader_name)s downloaded %(doc_title)s at %(time)s") % {
			"downloader_name": self.display_name(),
			"doc_title": self.document.title,
			"time": self.time_string_l(),
		}
	
	def display_name(self):
		return self.downloader.egghead.display_name()

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

class IDocRating(models.Model):
	rater				= models.ForeignKey(User)
	rating              = models.IntegerField()
	document			= models.ForeignKey(IDocument)
	time_stamp			= models.DateTimeField()

	def __unicode__(self):
		return _("%(rater_name)s gives %(doc_title)s a rating of %(rating)d at %(time)s") % {
			"rater_name": self.display_name(),
			"doc_title": self.document.title,
			"rating": self.rating,
			"time": self.time_string_l()
		}

	def display_name(self):
		return self.rater.egghead.display_name()

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")
	def time_string_date(self):
		return self.time_stamp.strftime("%Y %m-%d")

from worldbank.models import FreezeCredit, Transaction
class IDocFreezeCredit(FreezeCredit):
	idocument			= models.ForeignKey(IDocument, blank=True, null=True)
	idocrequest			= models.ForeignKey(IDocRequest, blank=True, null=True)
	def __unicode__(self):
		if self.ftype == "F":
			astring = _(u"[ iDoc ] %(time)s: %(amount)s points frozen from %(username)s's account") % {
				"time": self.time_string_l(),
				"amount": self.amount,
				"username": self.fuser.egghead.display_name()
			}
		else:
			astring = _(u"[ iDoc ] %(time)s: %(amount)d points unfrozen to %(username)s's account") % {
				"time": self.time_string_l(),
				"amount": self.amount,
				"username": self.fuser.egghead.display_name()
			}
		if self.ttype == "DRD":
			bstring = _(u"Requesting a document: %(docrequest_title)s") % {"docrequest_title": self.idocrequest.title}
		else:
			bstring = _(u"Unknown reason")
		# return string_concat(astring, " - ", bstring)
		return u"%s - %s" % (astring, bstring)
			

	def copy_unfreeze(self):
		ufc = IDocFreezeCredit(time_stamp=datetime.now(), fuser=self.fuser, ftype="U",
			app=self.app, ttype=self.ttype, amount=self.amount, cleared=True, 
			idocument=self.idocument, idocrequest=self.idocrequest)
		ufc.save()

class IDocTransaction(Transaction):
	idocument			= models.ForeignKey(IDocument)
	def __unicode__(self):
		if self.flow_type == "B":
			astring = _("[ iDoc ] %(time)s: %(amount)d points awarded to %(receiver_name)s") % {
				"time": self.time_string_l(),
				"amount": self.amount,
				"receiver_name": self.dst.egghead.display_name()
			}
			if self.ttype == "DUD":
				bstring = _("Uploading a document: %(doc_title)s") % {"doc_title": self.idocument.title}
			else:
				bstring = _("Unknown reason")
		else:
			astring = _("[ iDoc ] %(time)s: %(amount)d points transfered from %(sender_name)s to %(receiver_name)s") % {
				"time": self.time_string_l(),
				"amount": self.amount,
				"sender_name": self.src.egghead.display_name(),
				"receiver_name": self.dst.egghead.display_name()
			}
			if self.ttype == "DDD":
				bstring = _("Downloading the document: %(doc_title)s") % {"doc_title": self.idocument.title}
			else:
				bstring = _("Unknown reason")
		return u"%s - %s" % (astring, bstring)

	def src_name(self):
		if self.flow_type == "B": 
			if not self.src:
				return _("World Bank")
			else:
				return self.src.egghead.display_name()
		else:
			if self.ttype == "DDD":
				return self.src.egghead.display_name()
			else:
				return _("Unknown")

	def dst_name(self):
		if self.flow_type == "B": 
			if not self.dst:
				return _("World Bank")
			else:
				return self.dst.egghead.display_name()
		else:
			if self.ttype == "DDD":
				return self.dst.egghead.display_name()
			else:
				return _("Unknown")

	def reason(self):
		if self.ttype == "DUD":	
			return _("Uploading a document: '%(doc_title)s'") % {"doc_title": self.idocument.title}
		elif self.ttype == "DDD":
			return _("Downloading the document: '%(doc_title)s'") % {"doc_title": self.idocument.title}
		else:
			return _("idoc transactions")












