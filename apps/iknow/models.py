from django.db import models
from django.db.models import Sum, Avg
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import loader, Context
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime, timedelta
import math
import logging
from core.models import ICoreCategory, IComment, MasterPiece
from core.utils import show_name

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
	from django.core.mail import send_mail
from core.utils import verified_emails

klogger = logging.getLogger("pwe.iknow")

# Create your models here.
class QuestionTag(models.Model):
	name				= models.CharField(max_length=32)
	parent				= models.ForeignKey("self", blank=True, null=True)
	count				= models.IntegerField(default=1)

	def __unicode__(self):
		return self.name

	def update_count(self):
		self.count = self.count + 1
		self.save()

class Question(models.Model):
	QUESTION_STATUS = (
		("A", _("Active")),
		("W", _("Withdrawn")),
		("P", _("Expired and Pending")),
		("F", _("Expired and Forfeited")),
		("S", _("Solved and Closed")),
		("U", _("Unsolved and Closed")),
		("E", _("Extended")),
		("I", _("Illegal")),
	)
	SHARING_OPTIONS = (
		("P", _("Public")),
		("F", _("Friends")),
		("G", _("Groups")),
		("B", _("Both friends and selected groups")),
		("U", _("Targeted Users")),
	)
	asker				= models.ForeignKey(User, related_name="questions_asked")
	time_stamp			= models.DateTimeField()

	question_title		= models.CharField(max_length=128)
	question_text		= models.TextField(blank=True)
	anonymous			= models.BooleanField(default=False)
	hide_answers		= models.BooleanField(default=False)

	points_offered		= models.IntegerField(default=0)
	points_final		= models.IntegerField(default=0)
	points_expiration	= models.DateTimeField(blank=True, null=True)

	tags				= models.CharField(max_length=512, blank=True)
	categories			= models.ManyToManyField(ICoreCategory, blank=True, null=True)

	status				= models.CharField(max_length=1, choices=QUESTION_STATUS, default="A")
	sharing				= models.CharField(max_length=1, choices=SHARING_OPTIONS, default="P")

	thumb_up			= models.IntegerField(default=0)
	thumb_down			= models.IntegerField(default=0)

	thumbs				= models.IntegerField(default=0, blank=True, null=True)

	to_users			= models.ManyToManyField(User, related_name="questions_received",
							blank=True, null=True)
	to_groups			= models.ManyToManyField("tribes.Tribe", blank=True, null=True)
	visits				= models.IntegerField(default=0)

	def __unicode__(self):
		if self.rewarding():
			if self.points_final:
				return self.question_title + " (" + str(self.points_final) + ")"
			else:
				return self.question_title + " (" + str(self.points_offered) + ")"
		else:	
			return self.question_title
	
	def get_absolute_url(self):
		return reverse("iknow_question", kwargs={"question_id": self.id})
	
	def is_answered_by(self, user):
		try:
			Answer.objects.get(question=self, answerer=user)
			return True
		except Exception, e:
			return False
	
	def answerable(self):
		return self.status in ["A", "E"]
	
	def points_allocatable(self):
		return self.status in ["A", "E", "P"] and self.rewarding()

	def force_expire(self):
		self.points_expiration = datetime.now()
		self.save()
		self.update_time()

	def update_time(self):
		if not self.rewarding() and self.status == "A":
			if self.points_expiration and self.points_expiration < datetime.now():
				if self.answer_set.all():
					self.status = "S"
				else:
					self.status = "U"
				self.save()
		if self.points_allocatable() and self.points_expiration < datetime.now():
			if self.status == "A":
				if self.points_expiration + timedelta(days=2) < datetime.now():
					self.forfeit()
				else:
					self.status = "P"
					self.save()
					recipients = (self.asker, )
					current_site = Site.objects.get_current()
					subject = u"[ %s ] %s" % (current_site.name, _("Action is needed on your question"))
					t = loader.get_template("iknow/question_pending.txt")
					c = Context({
							"question": self,
							"current_site": current_site,
						})
					send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))
			elif self.status == "E":
				self.forfeit()
			elif self.status == "P":
				if self.points_expiration + timedelta(days=2) < datetime.now():
					self.forfeit()
	
	def forfeit(self):
		self.status = "F"
		self.save()
		try: 
			from worldbank.models import FreezeCredit, Transaction
			from egghead.models import get_egghead_from_user
			if not self.rewarding():
				return
			freezecredit = FreezeCredit.objects.get(fuser=self.asker, ftype="F", question=self)
			freezecredit.unfreeze()
			if self.answer_count() > 0:
				slice = int(math.floor(self.points_offered *  1.0 / self.answer_count()))
				remainder = self.points_offered - slice * self.answer_count()
				for answer in self.answer_set.all():
					answer.points_received = slice
					answer.save()
					transaction = Transaction(time_stamp=datetime.now(), flow_type="I", src=self.asker,
						dst=answer.answerer, app="K", ttype="QA", amount=slice, question=self)
					transaction.save()
					transaction.execute()
				if remainder > 0:
					transaction = Transaction(time_stamp=datetime.now(), flow_type="B", src=self.asker,
						app="K", ttype="FO", amount=remainder, question=self)
					transaction.save()
					transaction.execute()
		except Exception, e:
			klogger.warning("Forfeit error: %s" % e)	

	def update_thumbs(self):
		thumbs = self.thumb_up - self.thumb_down
		self.thumbs = thumbs
		self.save()
	
	def update_visits(self):
		self.visits = self.visits + 1
		self.save()

	def get_answers(self, standard=None):
		if not standard:
			return self.answer_set.order_by("-time_stamp")
		elif standard == "thumbs":
			return self.answer_set.order_by("-points_received", "-thumbs", "-time_stamp")
		return self.answer_set.order_by("-time_stamp")
	
	def answer_count(self):
		return self.answer_set.count()
	
	def extend_expiration(self, days=7):
		if self.rewarding() and self.status in ("A", "P"):
			self.status = "E"
			self.points_expiration = self.points_expiration + timedelta(days=days)
			self.save()

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def date_string(self):
		return self.time_stamp.strftime("%Y-%m-%d")

	def expiration_string_l(self):
		return self.points_expiration.strftime("%Y-%m-%d,%I:%M%p")

	def deadline_string_l(self):
		if self.status == "P":
			deadline = self.points_expiration + timedelta(days=2)
		elif self.status == "E":
			deadline = self.points_expiration
		return deadline.strftime("%m-%d %I:%M%p")

	def time_left_string(self):
		# if not self.rewarding():
			# return "Unlimited"
		self.update_time()
		if self.status == "F":
			return _("Forfeited")
		elif self.status == "U":
			return _("Unsolved")
		elif self.status == "P":
			return _("Expired and Pending")
		elif self.status == "S":
			return _("Solved")
		elif self.answerable():
			delta = self.points_expiration - datetime.now()
			days = delta.days
			seconds = delta.seconds
			hours = int(seconds) / 3600
			if days > 0:
				days_part = ungettext_lazy("%(count)d day", "%(count)d days", days) % {"count":days}
				hours_part = ungettext_lazy("%(count)d hr", "%(count)d hrs", hours) % {"count":hours}
				return string_concat(days_part, " ", hours_part)
			else:
				minutes = int(seconds - hours * 3600) / 60
				if hours > 0:
					hours_part = ungettext_lazy("%(count)d hr", "%(count)d hrs", hours) % {"count":hours}
					mins_part = ungettext_lazy("%(count)d min", "%(count)d mins", minutes) % {"count":minutes}
					return string_concat(hours_part, " ", mins_part)
				else:
					return ungettext_lazy("%(count)d min", "%(count)d mins", minutes) % {"count": minutes}
	
	def display_name(self):
		if self.anonymous:
			return _("An Egghead")
		else:
			return show_name(self.asker)

	def rewarding(self):
		if self.points_final:
			return True
		return self.points_offered > 0

	def comment_count(self):
		return self.questioncomment_set.count()

	def comments(self):
		return self.questioncomment_set.filter(deleted=False).order_by("-time_stamp")

class QuestionAmendment(MasterPiece):
	question			= models.ForeignKey(Question)
	def __unicode__(self):
		return _("Amendment made on question: %(question_title)s at %(time_stamp)s") % {
			"question_title": self.question.question_title, 
			"time_stamp": self.time_stamp
		}

class QuestionFavorite(models.Model):
	adder				= models.ForeignKey(User)
	question			= models.ForeignKey(Question)
	deleted				= models.BooleanField(default=False)
	time_stamp			= models.DateTimeField()

	def __unicode__ (self):
		return show_name(self.adder) + " : " + self.question.question_title
	

class Answer(models.Model):
	ANSWER_STATUS = (
		("R", _("Regular")),
		("E", _("Edited")),
		("I", _("Illegal")),
		("W", _("Withdrawn")),
	)
	SHARING_OPTIONS = (
		("P", _("Public")),
		("F", _("Friends")),
		("G", _("Groups")),
		("B", _("Both friends and selected groups")),
		("U", _("Targeted Users")),
		("A", _("Asker")),
	)
	answerer			= models.ForeignKey(User, related_name="answers_answered")	
	question			= models.ForeignKey(Question)
	time_stamp			= models.DateTimeField()
	edit_time_stamp		= models.DateTimeField(blank=True, null=True)
	answer_text			= models.TextField()
	tags				= models.CharField(max_length=512, blank=True)
	status				= models.CharField(max_length=1, choices=ANSWER_STATUS, default="R")
	sharing				= models.CharField(max_length=1, choices=SHARING_OPTIONS, default="P")
	thumb_up			= models.IntegerField(default=0)
	thumb_down			= models.IntegerField(default=0)
	thumbs				= models.IntegerField(default=0, blank=True, null=True)
	rating_by_asker		= models.IntegerField(default=-1)
	anonymous			= models.BooleanField(default=False)
	points_received		= models.IntegerField(default=0)

	to_users			= models.ManyToManyField(User, related_name="answers_shared", blank=True, null=True)
	to_groups			= models.ManyToManyField("tribes.Tribe", blank=True, null=True)

	picture				= models.ImageField(upload_to="iknow/answers/pictures/%Y/%m/%d/", 
							verbose_name=_("Picture"),
							blank=True, null=True)

	hidden				= models.BooleanField(default=False)

	file				= models.FileField(upload_to="iknow/answers/files/%Y/%m/%d/", 
							blank=True, null=True)
	visits				= models.IntegerField(default=0)

	def __unicode__(self):
		return self.answer_text
			
	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def edit_time_string_l(self):
		return self.edit_time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def update_thumbs(self):
		thumbs = self.thumb_up - self.thumb_down
		self.thumbs = thumbs
		self.save()
	
	def protected(self):
		hidden = self.hidden or self.question.hide_answers
		return self.question.answerable() and hidden

	def display_name(self):
		if self.anonymous:
			return _("An Egghead")
		else:
			return show_name(self.answerer)

	def received_tipping_times(self):
		from worldbank.models import Transaction
		return Transaction.objects.filter(
				flow_type = "I",
				dst = self.answerer,
				app = "K",
				ttype = "TI",
				question = self.question).count()

	def received_tipping_total(self):
		from worldbank.models import Transaction
		return Transaction.objects.filter(
				flow_type = "I",
				dst = self.answerer,
				app = "K",
				ttype = "TI",
				question = self.question).aggregate(total=Sum("amount"))["total"]

	def comment_count(self):
		return self.answercomment_set.count()

	def comments(self):
		return self.answercomment_set.filter(deleted=False).order_by("-time_stamp")


class Rating(models.Model):
	TYPE_CHOICES = (
		("E", _("As a elicitor")),
		("C", _("As a contributor")),
	)
	rater				= models.ForeignKey(User, related_name="iknow_rating_given")
	receiver			= models.ForeignKey(User, related_name="iknow_rating_received")
	rating              = models.DecimalField(max_digits=4, decimal_places=2)
	question			= models.ForeignKey(Question)
	rtype				= models.CharField(max_length=1, choices=TYPE_CHOICES)
	time_stamp			= models.DateTimeField()

	def __unicode__(self):
		return _("%(rater_name)s gives %(receiver_name)s a %(rating)s rating on question '%(question_title)s'") % {
			"rater_name": show_name(self.rater),
			"receiver_name": show_name(self.receiver),
			"rating": self.rating,
			"question_title": self.question.question_title,
		}

class QuestionComment(IComment):
	question			= models.ForeignKey(Question)
	
	def __unicode__(self):
		return _("%(commentor)s's comment on question: '%(question_title)s'") % {
			"commentor": show_name(self.creator),
			"question_title": self.question.question_title
		}

class AnswerTip(models.Model):
	answer				= models.ForeignKey(Answer)
	tipper				= models.ForeignKey(User)
	time_stamp			= models.DateTimeField()
	amount				= models.IntegerField(default=1)

	def __unicode__(self):
		return _("%(tipper_name)s tips %(answerer_name)s %(amount)d points for an answer to the question '%(question_title)s'") %{
			"tipper_name": show_name(self.tipper),
			"answerer_name": show_name(self.answer.answerer),
			"amount": self.amount,
			"question_title": self.answer.question.question_title,
		}

	def tipper_name(self):
		return show_name(self.tipper)

	def transfer(self):
		from worldbank.models import Transaction
		transaction = Transaction(time_stamp=self.time_stamp,
						flow_type = "I",
						src = self.tipper,
						dst = self.answer.answerer,
						app = "K",
						ttype = "TI",
						amount = self.amount,
						question = self.answer.question)
		transaction.save()
		transaction.execute()

class AnswerComment(IComment):
	answer				= models.ForeignKey(Answer)
	tip					= models.ForeignKey(AnswerTip, blank=True, null=True)
	
	def __unicode__(self):
		return _("%(commentor)s's comment on %(answerer_name)s's answer to the question: '%(question_title)s'") % {
			"commentor": show_name(self.creator),
			"answerer_name": show_name(self.answer.answerer),
			"question_title": self.answer.question.question_title
		}
	
class Thumb(models.Model):
	UP_DOWN_CHOICES = (
		("U", _("Thumb up")),
		("D", _("Thumb down")),
	)
	TYPE_CHOICES = (
		("Q", _("Question")),
		("A", _("Answer"))
	)
	thumber				= models.ForeignKey(User)
	up_or_down			= models.CharField(max_length=1, choices=UP_DOWN_CHOICES)
	type				= models.CharField(max_length=1, choices=TYPE_CHOICES)
	question			= models.ForeignKey(Question, blank=True, null=True)
	answer				= models.ForeignKey(Answer, blank=True, null=True)
	time_stamp			= models.DateTimeField()

	def __unicode__ (self):
		if self.type == "Q":
			if self.up_or_down == "U":
				return _("%(thumber_name)s thumbs up on %(asker_name)s's question: '%(question_title)s'") % {
					"thumber_name": show_name(self.thumber),
					"asker_name": show_name(self.question.asker),
					"question_title": self.question.question_title
				}
			else:
				return _("%(thumber_name)s thumbs down on %(asker_name)s's question: '%(question_title)s'") % {
					"thumber_name": show_name(self.thumber),
					"asker_name": show_name(self.question.asker),
					"question_title": self.question.question_title
				}
		else:
			if self.up_or_down == "U":
				return _("%(thumber_name)s thumbs up on %(answerer_name)s's answer to the question: '%(question_title)s'") % {
					"thumber_name": show_name(self.thumber),
					"answerer_name": show_name(self.answer.answerer),
					"question_title": self.answer.question.question_title
				}
			else:
				return _("%(thumber_name)s thumbs down on %(answerer_name)s's answer to the question: '%(question_title)s'") % {
					"thumber_name": show_name(self.thumber),
					"answerer_name": show_name(self.answer.answerer),
					"question_title": self.answer.question.question_title
				}

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")
	

