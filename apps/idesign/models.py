from django.db import models
from django.db.models import Sum, Avg
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from datetime import datetime, timedelta
import math
import logging
from core.utils import show_name

from core.models import MasterPiece, IThumb, IDonate
from worldbank.models import Transaction, FreezeCredit

# Create your models here.
class DesignIdea(MasterPiece):
	STATUS_OPTIONS = (
		("A", "Active"),
		("E", "Extended"),
		("F", "Fulfilled"),
		("P", "Partially Fulfilled"),
		("U", "Left alone"),
	)
	status				= models.CharField(max_length=1, choices=STATUS_OPTIONS, default="A")

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("idesign_designidea", kwargs={"designidea_id": self.id})
	
	def total_award(self):
		donation = self.designideadonate_set.aggregate(total=Sum("amount"))["total"]
		if not donation: donation = 0
		return donation + self.points_offered
	
	def update_points_final(self):
		self.points_final = self.total_award()
		self.save()

	def update_thumbs(self):
		self.thumb_up = self.designideathumb_set.filter(designidea=self, up_or_down="U").count()
		self.thumb_down = self.designideathumb_set.filter(designidea=self, up_or_down="D").count()
		self.thumbs = self.thumb_up - self.thumb_down
		self.save()

class DesignIdeaThumb(IThumb):
	designidea			= models.ForeignKey(DesignIdea)

	def __unicode__(self):
		if self.up_or_down == "U":
			return show_name(self.thumber) + "thumbs up on " + self.designidea.title
		else:
			return show_name(self.thumber) + "thumbs down on " + self.designidea.title

class DesignIdeaDonate(IDonate):
	designidea			= models.ForeignKey(DesignIdea)
	def __unicode__(self):
		return "%s donated %d points on %s" % (show_name(self.donater), self.amount, self.designidea)
	

class DesignIdeaFreezeCredit(FreezeCredit):
	designidea			= models.ForeignKey(DesignIdea)
	is_donate			= models.BooleanField(default=False)
	def __unicode__ (self):
		if self.ttype == "DS":
			if self.ftype == "F":
				if self.is_donate:
					return _("[ iDesign ] %(time)s: %(amount)d points frozen from %(user_name)s's account for donating on the design idea '%(designidea)s'") % {
							"time": self.time_string_l(),
							"amount": self.amount,
							"user_name": self.fuser.egghead.display_name(),
							"designidea": self.designidea.title
						}
				else:
					return _("[ iDesign ] %(time)s: %(amount)d points frozen from %(user_name)s's account for proposing a new design idea '%(designidea)s'") % {
							"time": self.time_string_l(),
							"amount": self.amount,
							"user_name": self.fuser.egghead.display_name(),
							"designidea": self.designidea.title
						}
			else:
				if self.is_donate:
					return _("[ iDesign ] %(time)s: %(amount)d points unfrozen to %(user_name)s's account for donating on the design idea '%(designidea)s'") % {
							"time": self.time_string_l(),
							"amount": self.amount,
							"user_name": self.fuser.egghead.display_name(),
							"designidea": self.designidea.title
						}
				else:
					return _("[ iDesign ] %(time)s: %(amount)d points unfrozen to %(user_name)s's account for proposing a new design idea '%(designidea)s'") % {
							"time": self.time_string_l(),
							"amount": self.amount,
							"user_name": self.fuser.egghead.display_name(),
							"designidea": self.designidea.title
						}

	def copy_unfreeze(self):
		ufca = DesignIdeaFreezeCredit(time_stamp=datetime.now(), fuser=self.fuser, ftype="U", is_donate=self.is_donate,
			app=self.app, ttype=self.ttype, amount=self.amount, cleared=True, designidea=self.designidea)
		ufca.save()
