from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Max, Min, Avg
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime
# Create your models here.

class EggHead(models.Model):
	# external foreign key to User
	user				= models.OneToOneField(User)

	unique_id			= models.CharField(max_length=20, blank=True)

	title				= models.CharField(max_length=64, blank=True)
	affiliation			= models.CharField(max_length=128, blank=True)
	program_year		= models.CharField(max_length=32, blank=True)

	gtalk				= models.EmailField(max_length=32, blank=True)
	facebook			= models.CharField(max_length=32, blank=True)
	twitter				= models.CharField(max_length=32, blank=True)

	expertise_tags		= models.TextField(blank=True)
	prior_experiences	= models.TextField(blank=True)

	geographic_interests	= models.CharField(max_length=256, blank=True)
	sector_interests	= models.CharField(max_length=512, blank=True)

	wealth_gold			= models.IntegerField(default=200, blank=True, null=True)
	wealth_notes		= models.IntegerField(default=2000, blank=True, null=True)

	elicitor_rating		= models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
	contributor_rating	= models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

	band				= models.IntegerField(default=0, blank=True, null=True)
	band_name			= models.CharField(default="newbie", max_length=32, blank=True)

	earning_total		= models.IntegerField(default=0, blank=True, null=True)
	activity_level		= models.IntegerField(default=0, blank=True, null=True)

	def __unicode__(self):
		return self.user.username
	
	def get_profile(self):
		return self.user.get_profile()

	def announcepost_thumbs(self, announcepost):
		return announcepost.announcepostthumb_set.filter(thumber=self.user).count()

	def total_income(self):
		isum = self.user.dst_transactions.aggregate(isum=Sum("amount"))["isum"]
		if not isum: isum = 0
		return isum

	def total_spending(self):
		osum = self.user.src_transactions.aggregate(osum=Sum("amount"))["osum"]
		if not osum: osum = 0
		return osum
	
	def update_record(self):
		self.earning_total = self.total_income()
		self.activity_level = self.earning_total + self.total_spending()
		self.save()
	
	def get_ranking_by_wealth(self):
		egghead_list = list(EggHead.objects.all().order_by("-wealth_notes"))
		return egghead_list.index(self)
	
	def get_percentage(self):
		rank = self.get_ranking_by_wealth()
		total = EggHead.objects.count()
		return 1 - rank * 1.0 / total

	def cal_elicitor_rating(self):
		rcount = self.elicitor_rating_count()
		if rcount == 0:
			return -1
		else:
			rating_list = [obj.rating for obj in self.user.rating_given.filter(rtype="E")]
			self.elicitor_rating = sum(rating_list) / rcount
			return self.elicitor_rating
	
	def display_name(self):
		if self.user.get_full_name():
			return self.user.get_full_name()
		else:
			return self.user.username

	def elicitor_rating_count(self):
		return self.user.rating_given.filter(rtype="E").count()

	def cal_contributor_rating(self):
		rcount = self.contributor_rating_count()
		if rcount == 0:
			return -1
		else:
			rating_list = [obj.rating for obj in self.user.rating_given.filter(rtype="C")]
			self.contributor_rating = sum(rating_list) / rcount
			return self.contributor_rating

	def contributor_rating_count(self):
		return self.user.rating_given.filter(rtype="C").count()
	
	def get_suggested_questions(self):
		questions = [question for question in Question.objects.exclude(asker=self.user).order_by("-time_stamp")
						if not question.is_answered_by(self.user)]
		return questions[:5]
	
	def frozen_credits(self):
		frozencredits = self.user.freezecredit_set.filter(cleared=False)\
			.aggregate(sum=Sum("amount"))["sum"]
		if not frozencredits: frozencredits = 0
		return frozencredits

	def frozen_bidding_credits(self):
		frozencredits = self.user.freezecredit_set.filter(app="A", ttype="BI", cleared=False)\
			.aggregate(sum=Sum("amount"))["sum"]
		if not frozencredits: frozencredits = 0
		return frozencredits

	def available_credits(self):
		return self.wealth_notes - self.frozen_credits()
	
	def bidding_credits(self):
		income_credits = max(self.total_income() - self.frozen_bidding_credits(), 0)
		return min(income_credits, self.available_credits())

	def get_questions_asked(self, max_item=8, purge_anonymous=False):
		if max_item >= 0 and not purge_anonymous:
			return self.user.questions_asked.order_by("-time_stamp")[:max_item]
		elif max_item < 0 and not purge_anonymous:
			return self.user.questions_asked.order_by("-time_stamp")
		elif max_item >= 0 and purge_anonymous:
			return self.user.questions_asked.filter(anonymous=False).order_by("-time_stamp")[:max_item]
		elif max_item < 0 and purge_anonymous:
			return self.user.questions_asked.filter(anonymous=False).order_by("-time_stamp")
	
	def get_questions_answered(self, max_item=6, purge_anonymous=False):
		if max_item >= 0 and not purge_anonymous:
			return self.user.answers_answered.order_by("-time_stamp")[:max_item]
		elif max_item < 0 and not purge_anonymous:
			return self.user.answers_answered.order_by("-time_stamp")
		elif max_item >= 0 and purge_anonymous:
			return self.user.answers_answered.filter(anonymous=False).order_by("-time_stamp")[:max_item]
		elif max_item < 0 and purge_anonymous:
			return self.user.answers_answered.filter(anonymous=False).order_by("-time_stamp")
	
	def count_questions_all(self):
		return self.user.questions_asked.count()

	def count_questions_solved(self):
		return self.user.questions_asked.filter(status="S").count()

	def count_questions_inmarket(self):
		return self.user.questions_asked.filter(status__in=("A", "E")).count()

	def count_answers_all(self):
		return self.user.answers_answered.count()

	def average_answer_rating(self):
		av_rating = self.user.answers_answered.filter(rating_by_asker__gt=0)\
			.aggregate(av=Avg("rating_by_asker"))["av"]
		if av_rating: 
			return "%.2f" % av_rating
		else:
			return _("N/A: No rated answers yet")

	def average_answer_thumbs(self):
		count = self.count_answers_all()
		if count == 0:
			return _("N/A: No answers yet")
		else:
			sum = 0
			for answer in self.user.answers_answered.all():
				sum = sum + answer.thumbs
			return "%.2f" % (sum * 1.0 / count)

	def count_answers_pos_points(self):
		return self.user.answers_answered.filter(points_received__gt=0).count()

	def total_answers_points(self):
		sum = 0
		for answer in self.user.answers_answered.filter(points_received__gt=0):
			sum = sum + answer.points_received
		return sum

	def has_question_as_favorite(self, question):
		try:
			qf = self.user.questionfavorite_set.get(question=question, deleted=False)
			return True
		except Exception, e:
			return False

	def add_question_as_favorite(self, question):
		qf, created = self.user.questionfavorite_set.get_or_create(question=question,
			defaults={"deleted": False, "time_stamp": datetime.now()})
		if not created:
			qf.deleted = False
			qf.save()

	def delete_question_as_favorite(self, question):
		try:
			qf = self.user.questionfavorite_set.get(question=question, deleted=False)
			qf.deleted = True
			qf.save()
		except Exception, e:
			pass

	def favorite_questions(self):
		return self.user.questionfavorite_set.filter(deleted=False).order_by("-time_stamp")
			
def get_egghead_from_user(user):
	try:
		egghead = user.egghead
	except Exception, e:
		egghead, created = EggHead.objects.get_or_create(user=user,
			defaults={
				"wealth_gold": 200,
				"wealth_notes": 2000,
				"band": 0,
				"band_name": "newbie",
			})
	return egghead

