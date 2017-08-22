from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from iknow.models import Question
from egghead.models import get_egghead_from_user
from datetime import datetime
# Create your models here.

	
class Transaction(models.Model):
	FLOW_TYPES = (
		("I", _("Individuals")),
		("B", _("Bank")),
	)
	Transaction_APPS = (
		("K", _("iKnow")),
		("D", _("iDoc")),
		("N", _("iNews")),
		("Q", _("iQuest")),
		("P", _("iPredict")),
		("I", _("iDea")),
		("S", _("Subsidize")),
	)
	Transaction_TYPES = (
		("LI", _("Log in")),
		# iKnow
		("QA", _("Question and Answer")),
		("TI", _("Tipping on Answers")),
		("FO", _("Forfeited by World Bank")),
		("TU", _("Thumb up or down")),
		("AC", _("Comment on Answers")),
		("KQC", _("Leave a comment to a question")),
		("KFQ", _("Ask the first question on Barter")),
		("AL", _("Allocate points")),
		# iDesign
		("DI", _("Propose a design idea")),
		# iDoc
		("DUD", _("Upload a new document")),
		("DDD", _("Download another user's document")),
		#iNews
		("NVU", _("Vote Up/Down an article")),
		("NVN", _("Post a new article")),
		# iDea
		("ITU", _("Thumb Up/Down on an idea")),
		("ITC", _("Thumb Up/Down on a comment to an idea")),
		("IRT", _("Rate an idea")),
		("IIC", _("Leave a comment on an idea")),
		("ITI", _("Tip the commentor to an idea")),
	)

	time_stamp			= models.DateTimeField()
	flow_type			= models.CharField(max_length=1, choices=FLOW_TYPES)
	src					= models.ForeignKey(User, blank=True, null=True, related_name="src_transactions")
	dst					= models.ForeignKey(User, blank=True, null=True, related_name="dst_transactions")
	app					= models.CharField(max_length=1, choices=Transaction_APPS)
	ttype				= models.CharField(max_length=3, choices=Transaction_TYPES)
	amount				= models.IntegerField(default=0)
	question			= models.ForeignKey(Question, blank=True, null=True)

	# __unicode__ and reason are a little redundant, reason is displayed on the transaction history page
	# __unicode__ is used primarily in the admin interface

	def __unicode__ (self):
		if hasattr(self, "idoctransaction"):
			return self.idoctransaction.__unicode__()
		if hasattr(self, "coolideatransaction"):
			return self.coolideatransaction.__unicode__()

		if self.app == "K":
			if self.ttype == "QA":
				return _("[ iKnow ] %(time)s: %(src_name)s transfers %(amount)d points to %(dst_name)s for answering the question '%(question_title)s'") % {
					"time": self.time_string_l(),
					"src_name": self.src.egghead.display_name(),
					"amount": self.amount,
					"dst_name": self.dst.egghead.display_name(),
					"question_title": self.question.question_title
				}
			elif self.ttype == "TI":
				return _("[ iKnow ] %(time)s: %(src_name)s tips %(amount)d points to %(dst_name)s for the answer to the question '%(question_title)s'") %{
					"time": self.time_string_l(),
					"src_name": self.src.egghead.display_name(),
					"amount": self.amount,
					"dst_name": self.dst.egghead.display_name(),
					"question_title": self.question.question_title
				}
			elif self.ttype == "FO":
				return _("[ iKnow ] %(time)s: %(src_name)s forfeits %(amount)d points to Worldbank for the question '%(question_title)s'") %{
					"time": self.time_string_l(),
					"src_name": self.src.egghead.display_name(),
					"amount": self.amount,
					"question_title": self.question.question_title
				}
			else:
				return _("Unknown iKnow transactions")

		if self.app == "D":
			# This branch should no longer be used by any transaction. It's kept here for uploading old documents FIXME
			if self.ttype == "DU":
				return _("[ iDoc - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for uploading the document '%(doc_title)s'") % {
						"time": self.time_string_l(),
						"dst_name": self.dst.egghead.display_name(),
						"amount": self.amount,
						"doc_title": self.document.title
					}
			else: 
				return _("Unknown iDoc transactions")

		if self.app == "S":
			if self.ttype == "LI":
				return _("[ System - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for logging in") % {
						"time": self.time_string_l(),
						"dst_name": self.dst.egghead.display_name(),
						"amount": self.amount
					}
			elif self.ttype == "TU":
				return _("[ iKnow - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for thumbing up/down on an answer to the question '%(question_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"question_title": self.question.question_title
				}
			elif self.ttype == "AC":
				return _("[ iKnow - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for commenting on an answer to the question '%(question_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"question_title": self.question.question_title
				}
			elif self.ttype == "AL":
				return _("[ iKnow - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for solving the question '%(question_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"question_title": self.question.question_title
				}
			elif self.ttype == "KQC":
				return _("[ iKnow - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for commenting on the question '%(question_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"question_title": self.question.question_title
				}
			elif self.ttype == "KFQ":
				return _("[ iKnow - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for asking the first question on Barter - '%(question_title)s'") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
					"question_title": self.question.question_title
				}
			# FIXME: This shouldn't be here.
			elif self.ttype == "DI":
				return _("[ iDesign - S ] %(time)s: %(dst_name)s is awarded %(amount)d points for proposing a new design idea") % {
					"time": self.time_string_l(),
					"dst_name": self.dst.egghead.display_name(),
					"amount": self.amount,
				}
			else:
				return _("Unknown transactions for system subsidy")

	def src_name(self):
		if self.flow_type == "B": 
			if not self.src:
				return _("World Bank")
			else:
				return self.src.egghead.display_name()
		else:
			if self.app == "K":
				if self.ttype == "QA":
					return self.question.display_name()
				elif self.ttype == "TI":
					return self.src.egghead.display_name()
			elif hasattr(self, "idoctransaction"):
				return self.idoctransaction.src_name()
			elif hasattr(self, "coolideatransaction"):
				return self.coolideatransaction.src_name()
			else:
				return _("Unknown")
	
	def dst_name(self):
		if self.flow_type == "B": 
			if not self.dst:
				return _("World Bank")
			else:
				return self.dst.egghead.display_name()
		else:
			if self.app == "K":
				return self.display_answerer_name()
			elif hasattr(self, "idoctransaction"):
				return self.idoctransaction.dst_name()
			elif hasattr(self, "coolideatransaction"):
				return self.coolideatransaction.dst_name()
			else:
				return _("Unknown")
	
	# This is what's displayed on the transaction page a user can see
	def reason(self):
		if hasattr(self, "idoctransaction"):
			return self.idoctransaction.reason()
		if hasattr(self, "coolideatransaction"):
			return self.coolideatransaction.reason()

		if self.app == "K":
			if self.ttype == "QA":
				return _("Answering the question '%(question_title)s'") % {
						"question_title": self.question.question_title,
					}
			elif self.ttype == "TI":
				return _("Tipping an answer to the question '%(question_title)s'") % {
						"question_title": self.question.question_title,
					}
			elif self.ttype == "FO":
				return _("Forfeit for question '%(question_title)s'") % {
						"question_title": self.question.question_title,
					}
			else:
				return _("Unknown iKnow transaction")
		if self.app == "D":
			if self.ttype == "DU":
				return _("Uploading a doc '%(doc_name)s'") % {"doc_name": self.document.title}
			else: 
				return _("Unknown iDoc transaction")
		if self.app == "S":
			if self.ttype == "LI":
				return _("Logging in on %(time)s") % {"time": self.time_stamp.strftime("%m-%d %I")}
			elif self.ttype == "TU":
				return _("Thumbing up/down on an answer to the question '%(question_title)s'") % { 
					"question_title": self.question.question_title,
				}
			elif self.ttype == "AC":
				return _("Commenting on an answer to the question '%(question_title)s'") % { 
					"question_title": self.question.question_title,
				}
			elif self.ttype == "AL":
				return _("25 %% refund for allocating points on time for the question '%(question_title)s'") % {
					"question_title": self.question.question_title,
				}
			elif self.ttype == "KQC":
				return _("Commenting on the question '%(question_title)s'") % { 
					"question_title": self.question.question_title,
				}
			elif self.ttype == "KFQ":
				return _("Asking the first question '%(question_title)s' on Barter") % { 
					"question_title": self.question.question_title,
				}
			# FIXME: This shouldn't be here.
			elif self.ttype == "DI":
				return _("Proposing a new design idea")
			else:
				return _("Unknown system subsidy transactions")

	def time_string_l(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def display_answerer_name(self):
		try:
			answer = self.dst.answers_answered.get(question=self.question)
			return answer.display_name()
		except Exception, e:
			return self.dst.egghead.display_name()
	
	def execute(self):
		if self.src:
			egghead_src = get_egghead_from_user(self.src)
			egghead_src.wealth_notes = egghead_src.wealth_notes - self.amount
			egghead_src.save()
			egghead_src.update_record()
		if self.dst:
			egghead_dst = get_egghead_from_user(self.dst)
			egghead_dst.wealth_notes = egghead_dst.wealth_notes + self.amount
			egghead_dst.save()
			egghead_dst.update_record()


class FreezeCredit(models.Model):
	FreezeTypes = (
		("F", _("Freeze")),
		("U", _("Unfreeze")),
	)
	Transaction_APPS = (
		("K", _("iKnow")),
		("O", _("iDoc")),
		("N", _("iNews")),
		("Q", _("iQuest")),
		("P", _("iPredict")),
		("I", _("iDea")),
		("A", _("iAuction")),
		("D", _("iDesign")),
	)
	Transaction_TYPES = (
		("QA", _("Question and Answer")),
		("BI", _("Bidding in iBay")),
		("DS", _("Design for self-Design")),
		("DRD", _("Request a document")),
		("IRC", _("Reward contributors to an idea")),
	)
	time_stamp			= models.DateTimeField()
	fuser				= models.ForeignKey(User)
	ftype				= models.CharField(max_length=1, choices=FreezeTypes)
	app					= models.CharField(max_length=1, choices=Transaction_APPS)
	ttype				= models.CharField(max_length=3, choices=Transaction_TYPES)
	amount				= models.IntegerField(default=0)
	question			= models.ForeignKey(Question, blank=True, null=True)
	cleared				= models.BooleanField(default=True)

	def __unicode__ (self):
		if hasattr(self, "freezecreditauction"):
			return self.freezecreditauction.__unicode__()
		elif hasattr(self, "freezecreditdesignidea"):
			return self.freezecreditdesignidea.__unicode__()
		elif hasattr(self, "idocfreezecredit"):
			return self.idocfreezecredit.__unicode__()
		elif hasattr(self, "coolideafreezecredit"):
			return self.coolideafreezecredit.__unicode__()
		if self.app == "K" and self.ttype == "QA":
			if self.ftype == "F":
				return _("[ iKnow ] %(time)s: %(amount)d points frozen from %(user_name)s's account for asking the question '%(question_title)s'") % {
						"time": self.time_string_l(),
						"amount": self.amount,
						"user_name": self.fuser.egghead.display_name(),
						"question_title": self.question.question_title
					}
			else:
				return _("[ iKnow ] %(time)s: %(amount)d points unfrozen to %(user_name)s's account for asking the question '%(question_title)s'") % {
						"time": self.time_string_l(),
						"amount": self.amount,
						"user_name": self.fuser.egghead.display_name(),
						"question_title": self.question.question_title
					}
		else:
			return _("Unknown credit freeze")
							

	def time_string_l(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def unfreeze(self):
		if self.ftype == "F" and not self.cleared:	
			self.cleared = True
			self.save()
			self.copy_unfreeze()
	
	def copy_unfreeze(self):
		ufc = FreezeCredit(time_stamp=datetime.now(), fuser=self.fuser, ftype="U",
			app=self.app, ttype=self.ttype, amount=self.amount, cleared=True, question=self.question)
		ufc.save()
			


