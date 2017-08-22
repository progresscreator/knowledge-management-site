from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime, timedelta
from core.models import MasterPiece, IThumb, IComment
from worldbank.models import FreezeCredit, Transaction
from django.core.urlresolvers import reverse

class CoolIdeaRequest(MasterPiece):
	pass

class CoolIdea(MasterPiece):
	STATUS_OPTIONS = (
		("A", _("Active")),
		("E", _("Extended")),
		("C", _("Closed")),
	)
	status				= models.CharField(max_length=1, choices=STATUS_OPTIONS, default="A")
	idea_level			= models.IntegerField(default=1)	
	version				= models.CharField(max_length=10, blank=True)
	rating				= models.FloatField(default=0)
	idearequest			= models.ForeignKey(CoolIdeaRequest, blank=True, null=True)

	collaborators		= models.ManyToManyField(User, blank=True, null=True, 
									related_name="ideas_involved")
	external_col		= models.CharField(max_length=512, blank=True)

	# An idea can be associated with pictures and files
	file1				= models.FileField(upload_to="idea/files/%Y/%m/%d/", blank=True,null=True)
	file2				= models.FileField(upload_to="idea/files/%Y/%m/%d/", blank=True,null=True)
	file3				= models.FileField(upload_to="idea/files/%Y/%m/%d/", blank=True,null=True)
	picture1			= models.ImageField(upload_to="idea/pictures/%Y/%m/%d/", blank=True, null=True)
	picture2			= models.ImageField(upload_to="idea/pictures/%Y/%m/%d/", blank=True, null=True)

	def get_absolute_url(self):
		return reverse("idea_coolidea", kwargs={"coolidea_id": self.id})

	def people_names(self):
		names = [self.creator.egghead.display_name(),]
		for user in self.collaborators.all():
			names.append(user.egghead.display_name())
		return ", ".join(names)

	def file1_name(self):
		full_name = self.file1.name
		r_ind = full_name.rfind("/")
		return full_name[r_ind+1:]

	def file2_name(self):
		full_name = self.file2.name
		r_ind = full_name.rfind("/")
		return full_name[r_ind+1:]

	def file3_name(self):
		full_name = self.file3.name
		r_ind = full_name.rfind("/")
		return full_name[r_ind+1:]

	def update_thumbs(self):
		self.thumb_up = self.coolideathumb_set.filter(coolidea=self, up_or_down="U").count()
		self.thumb_down = self.coolideathumb_set.filter(coolidea=self, up_or_down="D").count()
		self.thumbs = self.thumb_up - self.thumb_down
		self.save()

	def rating_string(self):
		if not self.coolidearating_set.all():
			return _("N/A")
		return "%.1f" % self.rating

	def update_rating(self):
		if not self.coolidearating_set.all():
			self.rating = 0
		else: 
			from django.db.models import Avg
			self.rating = self.coolidearating_set.aggregate(Avg("rating"))["rating__avg"]
		self.save()
	
	def comments_count(self):
		return self.coolideacomment_set.count()

class CoolIdeaThumb(IThumb):
	coolidea			= models.ForeignKey(CoolIdea)

	def __unicode__(self):
		if self.up_or_down == "U":
			return _("%(thumber_name)s thumbs up on %(idea_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"idea_title": self.coolidea.title
				}
		else:
			return _("%(thumber_name)s thumbs down on %(idea_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"idea_title": self.coolidea.title
				}

class CoolIdeaRating(models.Model):
	rater				= models.ForeignKey(User, related_name="ratings_on_coolideas")
	rating              = models.IntegerField()
	coolidea			= models.ForeignKey(CoolIdea)
	time_stamp			= models.DateTimeField()

	def __unicode__(self):
		return _("%(rater_name)s gives %(idea_title)s a rating of %(rating)d") % {
				"rater_name": self.rater.egghead.display_name(),
				"idea_title": self.coolidea.title,
				"rating": self.rating,
			}

	def display_name(self):
		return self.rater.egghead.display_name()

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def time_string_date(self):
		return self.time_stamp.strftime("%Y %m-%d")

class CoolIdeaComment(IComment):
	coolidea			= models.ForeignKey(CoolIdea)
	
	def __unicode__(self):
		return _("%(commentor_name)s comments on the idea %(idea_title)s") % {
				"commentor_name": self.display_name(),
				"idea_title": self.coolidea.title
			}

	def commenter_rating(self):
		try:
			return self.coolidea.coolidearating_set.get(rater=self.creator)
		except Exception, e:
			return None

	def commenter_thumb(self):
		try:
			return self.coolidea.coolideathumb_set.get(thumber=self.creator)
		except Exception, e:
			return None


class CoolIdeaCommentThumb(IThumb):
	comment				= models.ForeignKey(CoolIdeaComment)
	def __unicode__(self):
		if self.up_or_down == "U":
			return _("%(thumber_name)s thumbs up on %(commentor_name)s's comment on %(idea_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"commentor_name": self.comment.creator.egghead.display_name(),
					"idea_title": self.coolidea.title
				}
		else:
			return _("%(thumber_name)s thumbs down on %(commentor_name)s's comment on %(idea_title)s") % {
					"thumber_name": self.thumber.egghead.display_name(),
					"commentor_name": self.comment.creator.egghead.display_name(),
					"idea_title": self.coolidea.title
				}


class CoolIdeaCommentTip(models.Model):
	comment				= models.ForeignKey(CoolIdeaComment)
	tipper				= models.ForeignKey(User)
	time_stamp			= models.DateTimeField()
	amount				= models.IntegerField(default=1)
	def __unicode__(self):
		return _("Comment tip")

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def date_string(self):
		return self.time_stamp.strftime("%Y-%m-%d")

class CoolIdeaFreezeCredit(FreezeCredit):
	coolidea			= models.ForeignKey(CoolIdea, blank=True, null=True)
	idearequest			= models.ForeignKey(CoolIdeaRequest, blank=True, null=True)

	def __unicode__(self):
		if self.ttype == "IRC":
			if self.ftype == "F":
				return _("[ iDea ] %(time)s: %(amount)d points frozen from %(user_name)s's account for rewarding contributors to the idea '%(idea_name)s'") % {
						"time": self.time_string_l(),
						"amount": self.amount,
						"user_name": self.fuser.egghead.display_name(),
						"idea_name": self.coolidea.title
					}
			else:
				return _("[ iDea ] %(time)s: %(amount)d points unfrozen to %(user_name)s's account for rewarding contributors to the idea '%(idea_name)s'") % {
						"time": self.time_string_l(),
						"amount": self.amount,
						"user_name": self.fuser.egghead.display_name(),
						"idea_name": self.coolidea.title
					}

	def copy_unfreeze(self):
		ufc = CoolIdeaFreezeCredit(time_stamp=datetime.now(), fuser=self.fuser, ftype="U",
			app=self.app, ttype=self.ttype, amount=self.amount, cleared=True, 
			coolidea=self.coolidea, idearequest=self.idearequest)
		ufc.save()

class CoolIdeaTransaction(Transaction):
	coolidea			= models.ForeignKey(CoolIdea, blank=True, null=True)
	idearequest			= models.ForeignKey(CoolIdeaRequest, blank=True, null=True)
	coolideacomment		= models.ForeignKey(CoolIdeaComment, blank=True, null=True)
	def __unicode__(self):
		if self.ttype == "ITU":
			return _("[ iDea - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for thumbing up/down on the idea '%(idea_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "IRT":
			return _("[ iDea - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for rating the idea '%(idea_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "IIC":
			return _("[ iDea - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for commenting on the idea '%(idea_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "ITC":
			return _("[ iDea - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for thumbing up/down on %(commentor_name)s's comment to the idea '%(idea_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"commentor_name": self.coolideacomment.creator.egghead.display_name(),
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "ITI":
			return _("[ iDea - S ] %(time)s: %(tipper_name)s tips %(dst_name)s %(amount)d points for the comment to the idea '%(idea_title)s'") % {
					"time": self.time_string_l(),
					"tipper_name": self.src.egghead.display_name(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"idea_title": self.coolidea.title
				}
		else: 
			return _("Unknown iDea transaction")

	def src_name(self):
		if self.flow_type == "B": 
			if not self.src:
				return _("World Bank")
			else:
				return self.src.egghead.display_name()
		else:
			if self.ttype == "ITI":
				return self.src.egghead.display_name()
			return _("Unknown")
	
	def dst_name(self):
		if self.flow_type == "B": 
			if not self.dst:
				return _("World Bank")
			else:
				return self.dst.egghead.display_name()
		else:
			if self.ttype == "ITI":
				return self.coolideacomment.display_name()
			return _("Unknown")

	def reason(self):
		if self.ttype == "ITU":
			return _("Thumbing up/down on the idea '%(idea_title)s'") % {
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "IRT":
			return _("Rating the idea '%(idea_title)s'") % {
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "IIC":
			return _("Commenting on the idea '%(idea_title)s'") % {
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "ITC":
			return _("Thumbing up/down on %(commentor_name)s's comment to the idea '%(idea_title)s'") % {
					"commentor_name": self.coolideacomment.creator.egghead.display_name(),
					"idea_title": self.coolidea.title
				}
		elif self.ttype == "ITI":
			return _("Tipping for the %(commentor_name)s's comment to the idea '%(idea_title)s'") % {
					"commentor_name": self.coolideacomment.creator.egghead.display_name(),
					"idea_title": self.coolidea.title
				}
		else: 
			return _("CoolIdea transactions")
