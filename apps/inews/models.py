from django.db import models
from django.db.models import Sum, Avg
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime, timedelta
import math
import logging

from core.models import MasterPiece, IThumb, IComment
from worldbank.models import Transaction, FreezeCredit

class NewsTag(models.Model):
	name				= models.CharField(max_length=32)
	parent				= models.ForeignKey("self", blank=True, null=True)
	count				= models.IntegerField(default=1)

	def __unicode__(self):
		return self.name

	def update_count(self):
		self.count = self.count + 1
		self.save()

class AnnouncePost(MasterPiece):
	STATUS_OPTIONS = (
		("A", "Active"),
		("S", "Stagnant"),
		("E", "Expired"),
	)
	budget			= models.IntegerField(default=0)
	date_check      = models.DateTimeField()
	points_per_view		= models.IntegerField(default=0) 
	status 			= models.CharField(max_length=1, choices=STATUS_OPTIONS, default="A")
	user_count		= models.IntegerField(default=0)
	url			= models.URLField(blank=True, null=True)
	

	def __unicode__(self):
		return self.title
	
	def get_absolute_url(self):
		return reverse("inews_announcepost", kwargs={"announcepost_id": self.id})
	
	def cost_function(self, n):
		"""A monotonically increasing function assigning a price to the number
		of thumbs a given users gives to a given AnnouncePost."""
		return round(pow(2,n) - 2/n)
		
	def get_thumb_price(self, user):
		n_thumbs = user.egghead.announcepost_thumbs(self) + 1
		return self.cost_function(n_thumbs)

	def get_next_thumb_price(self, user):
		n_thumbs = user.egghead.announcepost_thumbs(self)
		return self.cost_function(n_thumbs+1)

	def get_n_thumb_count(self, user):
		n_thumbs = user.egghead.announcepost_thumbs(self) + 1
		return (n_thumbs)

	def update_points_final(self):
		self.points_final = self.total_award()
		self.save()
		
	def update_thumbs(self):
		self.thumb_up = self.announcepostthumb_set.filter(announcepost=self, up_or_down="U").count()
		self.thumb_down = self.announcepostthumb_set.filter(announcepost=self, up_or_down="D").count()
		self.thumbs = self.thumb_up - self.thumb_down
		self.save()
		
	def update_time(self):
        # if the question is active
		if self.status == "A":
            # while datetime.now > last_date_checked:
			while (datetime.now() - timedelta(days=1)) > self.date_check:
					self.budget -= self.points_per_view
					self.date_check = self.date_check + timedelta(days=1)
					self.save()
                
        # if the post budget < 0
		if self.budget < 0:
			self.budget = 0
            
		if self.budget == 0:
			self.status = "E"
			
		self.save()

	def is_first_time_reader(self, user):
		if self.userrecord_set.filter(viewer=user):
			return False
		else:
			return True
	

class UserRecord(models.Model):
	announcepost	= models.ForeignKey(AnnouncePost)
	viewer			= models.ForeignKey(User)	
	time_stamp		= models.DateTimeField()
	# uid = models.CharField(max_length=300)

	def __unicode__(self): 
   		return self.announcepost.title

class AnnouncePostThumb(IThumb):
	announcepost = models.ForeignKey(AnnouncePost)

	def __unicode__(self):
		if self.up_or_down == "U":
			return _("%(thumber_name)s thumbs up on %(post_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"post_title": self.announcepost.title
				}
		else:
			return _("%(thumber_name)s thumbs down on %(post_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"post_title": self.announcepost.title
				}


class AnnouncePostTransaction(Transaction):
	announcepost			= models.ForeignKey(AnnouncePost)
	def __unicode__(self):

		# From Bank
		if self.flow_type == "B":
			astring = _("[ iNews ] %(time)s: %(amount)d points awarded to %(receiver_name)s") % {
				"time": self.time_string_l(),
				"amount": self.amount,
				"receiver_name": self.dst.egghead.display_name()
			}
		
			# To individual
			if self.ttype == "XXX":
				bstring = _("(No current transaction for this type): %(article_title)s") % {"article_title": self.announcepost.title}
			else:
				bstring = _("Unknown reason")
		# From User
		else:
			astring = _("[ iNews ] %(time)s: %(amount)d points transfered from %(sender_name)s to %(receiver_name)s") % {
				"time": self.time_string_l(),
				"amount": self.amount,
				"sender_name": self.src.egghead.display_name(),
				"receiver_name": self.dst.egghead.display_name()
			}

			# To bank because an article was uploaded
			if self.ttype == "NVN":
				bstring = _("New article posted: %(article_title)s") % {"article_title": self.announcepost.title}		
	
			# To individual x because a vote was cast on individual x's article
			elif self.ttype == "NVU":
				bstring = _("Voted on the article: %(article_title)s") % {"article_title": self.announcepost.title}
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
			if self.ttype == "NVN":
				return self.src.egghead.display_name()
			
			elif self.ttype == "NVU":
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
			if self.ttype == "NVN":
				return _("World Bank")

			elif self.ttype == "NVU":
				return self.dst.egghead.display_name()
			else:
				return _("Unknown")

	def reason(self):
		if self.ttype == "NVN":	
			return _("Posting a new article: '%(article_title)s'") % {"article_title": self.announcepost.title}
		elif self.ttype == "NVU":
			return _("Voting on an article: '%(article_title)s'") % {"article_title": self.announcepost.title}
		else:
			return _("inews transactions")


class AnnouncePostComment(IComment):
	announcepost			= models.ForeignKey(AnnouncePost)
	
	def __unicode__(self):
		return _("%(commentor_name)s comments on the article %(article_title)s") % {
				"commentor_name": self.display_name(),
				"article_title": self.announcepost.title
			}

	def commenter_rating(self):
		try:
			return self.announcepost.coolidearating_set.get(rater=self.creator)
		except Exception, e:
			return None

	def commenter_thumb(self):
		try:
			return self.announcepost.announcepostthumb_set.get(thumber=self.creator)
		except Exception, e:
			return None


class AnnouncePostCommentThumb(IThumb):
	comment				= models.ForeignKey(AnnouncePostComment)
	def __unicode__(self):
		if self.up_or_down == "U":
			return _("%(thumber_name)s thumbs up on %(commentor_name)s's comment on %(article_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"commentor_name": self.comment.creator.egghead.display_name(),
					"article_title": self.announcepost.title
				}
		else:
			return _("%(thumber_name)s thumbs down on %(commentor_name)s's comment on %(article_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"commentor_name": self.comment.creator.egghead.display_name(),
					"article_title": self.announcepost.title
				}


class AnnouncePostCommentTip(models.Model):
	comment				= models.ForeignKey(AnnouncePostComment)
	tipper				= models.ForeignKey(User)
	time_stamp			= models.DateTimeField()
	amount				= models.IntegerField(default=1)
	def __unicode__(self):
		return _("Comment tip")

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def date_string(self):
		return self.time_stamp.strftime("%Y-%m-%d")


