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
from worldbank.models import FreezeCredit, Transaction

# Create your models here.
class AuctionProduct(models.Model):
	TYPE_CHOICES = (
		("P", _("Real Product")),
		("A", _("Virtual Award"))
	)
	STATUS_CHOICES = (
		("A", _("Active")),
		("W", _("Withdrawn")),
		("P", _("Expired and Pending")),
		("S", _("Expired and Sold")),
		("U", _("Expired and Unwanted")),
		("F", _("Expired and Failed")),
	)
	seller				= models.ForeignKey(User, blank=True, null=True)
	name				= models.CharField(max_length=128)
	details				= models.TextField(blank=True)
	start_price			= models.IntegerField(default=0)
	virtual				= models.BooleanField(default=False)
	start_time			= models.DateTimeField()
	end_time			= models.DateTimeField()
	# The "type" field is added here for future extension
	# Currently it's a bit redundant 
	type				= models.CharField(max_length=1, choices=TYPE_CHOICES, default="P")
	status				= models.CharField(max_length=1, choices=STATUS_CHOICES, default="A")
	picture				= models.ImageField(upload_to="iauction/product/pictures/%Y/%m/%d/", blank=True, null=True)
	visits				= models.IntegerField(default=0)

	def __unicode__(self):
		return self.name
	
	def seller_name(self):
		return show_name(self.seller)

	def has_expired(self):
		return self.status in ("P", "S", "U", "F")

	def get_absolute_url(self):
		return reverse("iauction_product", kwargs={"product_id": self.id})

	def update_visits(self):
		self.visits += 1
		self.save()
	
	def current_price(self):
		if self.auctionbid_set.count() > 0:
			return self.auctionbid_set.order_by("-time_stamp")[0].amount
		return self.start_price
	
	def current_leader(self):
		if self.auctionbid_set.all() and self.status == "A":
			return self.auctionbid_set.order_by("-time_stamp")[0].bidder
		return None

	def force_expire(self):
		self.end_time = datetime.now()
		self.save()
		self.expire()

	def expire(self):
		if self.status == "A" and datetime.now() > self.end_time:
			if self.auctionbid_set.count() > 0:
				self.status = "P"
				success_bid = AuctionBid.objects.filter(product=self).order_by("-time_stamp")[0]
				deal = AuctionDeal(bid=success_bid, status="P", time_stamp=datetime.now())
				deal.save()
			else:
				self.status = "U"
			self.save()
	
	def is_withdrawable(self):
		return self.status == "A" and not self.auctionbid_set.all()

	def success_bid(self):
		if self.status in ("P", "S", "F"):
			deal = AuctionDeal.objects.get(bid__product=self)
			return deal.bid
		return None

	def deal(self):
		if self.status in ("P", "S", "F"):
			deal = AuctionDeal.objects.get(bid__product=self)
			return deal
		return None
	
	def total_bids(self):
		return self.auctionbid_set.count()

	def start_time_string_l(self):
		return self.start_time.strftime("%Y-%m-%d,%I:%M%p")

	def start_time_string_s(self):
		return self.start_time.strftime("%I:%M%p,%m/%d/%y")

	def end_time_string_l(self):
		return self.end_time.strftime("%Y-%m-%d,%I:%M%p")

	def time_left_string(self):
		self.expire()
		if self.status == "A":
			delta = self.end_time - datetime.now()
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
		else:
			return _("Expired")
	
class AuctionBid(models.Model):
	product				= models.ForeignKey(AuctionProduct)
	bidder				= models.ForeignKey(User)
	amount				= models.IntegerField()
	time_stamp			= models.DateTimeField()
	anonymous			= models.BooleanField(default=False)
	win					= models.BooleanField(default=False)

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")
	
	def display_name(self):
		if self.anonymous:
			return _("An Egghead")
		else:
			return show_name(self.bidder)

	def __unicode__(self):
		return _("%(bidder_name)s bids %(amount)d points on '%(product)s' at %(time)s") % {
			"bidder_name": show_name(self.bidder),
			"amount": self.amount,
			"product": self.product.name,
			"time": self.time_string_l()
		}

class AuctionDeal(models.Model):
	STATUS_CHOICES = (
		("P", _("Pending")),
		("S", _("Successful")),
		("F", _("Failed")),
	)
	# bid contains all information we need
	bid					= models.ForeignKey(AuctionBid)
	status				= models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
	time_stamp			= models.DateTimeField()
	close_time			= models.DateTimeField(blank=True, null=True)
	cleared_by_seller	= models.BooleanField(default=False)
	cleared_by_winner	= models.BooleanField(default=False)

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")

	def status_string(self):
		if self.status == "P":
			return _("Pending")
		elif self.status == "S":
			return _("Transaction succesful")
		elif self.status == "F":
			return _("Transaction failed")
	
	def finalize(self):
		from worldbank.models import FreezeCreditAuction
		if self.cleared_by_seller and self.cleared_by_winner:
			for fca in FreezeCreditAuction.objects.filter(bid__product=self.bid.product,
				ftype="F", app="A", ttype="BI", cleared=False):
				fca.unfreeze()
			self.status = "S"
			self.close_time = datetime.now()
			self.save()
			self.bid.product.status = "S"
			self.bid.product.save()
			# transaction needs to be done
			# This is a rudimentary approach, must be fixed in future
			egghead_src = self.bid.bidder.egghead
			egghead_dst = self.bid.product.seller.egghead
			egghead_src.wealth_notes -= self.bid.amount
			egghead_dst.wealth_notes += self.bid.amount
			egghead_src.save()
			egghead_src.update_record()
			egghead_dst.save()
			egghead_dst.update_record()


	def __unicode__(self):
		return _("Deal: %(buyer)s spent %(amount)d on %(product)s at %(time)s") % {
			"buyer": show_name(self.bid.bidder),
			"amount": self.bid.amount,
			"product": self.bid.product.name,
			"time": self.time_string_l()
		}

class AuctionFreezeCredit(FreezeCredit):
	bid					= models.ForeignKey(AuctionBid)
	def __unicode__ (self):
		if self.ttype == "BI":
			if self.ftype == "F":
				return _("[ iBay ] %(time)s: %(amount)d points frozen from %(user_name)s's account for bidding on the product '%(product_name)s'") % {
						"time": self.time_string_l(),
						"amount": self.amount,
						"user_name": self.fuser.egghead.display_name(),
						"product_name": self.bid.product.name
					}
			else:
				return _("[ iBay ] %(time)s: %(amount)d points unfrozen to %(user_name)s's account for bidding on the product '%(product_name)s'") % {
						"time": self.time_string_l(),
						"amount": self.amount,
						"user_name": self.fuser.egghead.display_name(),
						"product_name": self.bid.product.name
					}

	def copy_unfreeze(self):
		ufca = AuctionFreezeCredit(time_stamp=datetime.now(), fuser=self.fuser, ftype="U",
			app=self.app, ttype=self.ttype, amount=self.amount, cleared=True, bid=self.bid)
		ufca.save()
