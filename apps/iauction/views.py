from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
	from django.core.mail import send_mail

from iauction.models import AuctionProduct, AuctionBid, AuctionDeal, AuctionFreezeCredit
from iauction.forms import AuctionProductForm
# from worldbank.models import FreezeCreditAuction
from core.utils import verified_emails

# Python libraries
import os
import logging
from datetime import datetime
from datetime import timedelta
import simplejson

alogger = logging.getLogger("pwe.iauction")

def iauction_home(request, template="iauction/iauction_home.html"):
	for product in AuctionProduct.objects.filter(status="A"):
		product.expire()
	recent_products = AuctionProduct.objects.filter(status="A")\
		.order_by("-start_time")[:24]
	my_products = set()
	for bid in AuctionBid.objects.filter(bidder=request.user, product__status="A").order_by("-product__end_time"):
		my_products |= set((bid.product, ))
	won_deals = AuctionDeal.objects.filter(bid__bidder=request.user).order_by("-bid__time_stamp")
	return render_to_response(template, 
				{"recent_products": recent_products,
				 "my_products": my_products,
				 "won_deals": won_deals,
				},
				context_instance=RequestContext(request))

def iauction_ajax_booth_products(request, username,
					status,
					page=1,
					order=None,
					template="iauction/iauction_ajax_booth_products.html"):
	buser = User.objects.get(username=username)
	products = AuctionProduct.objects.filter(seller=buser, status=status)
	if not order:
		products = products.order_by("-start_time")
	paginator = Paginator(products, 25)
	return render_to_response(template, 
				{
					"buser": buser,
					"products_page": paginator.page(page),
				},
				context_instance=RequestContext(request))

def iauction_booth(request, 
					  username,
					  template="iauction/iauction_booth.html"):
	buser = User.objects.get(username=username)
	return render_to_response(template, 
				{
					"buser": buser,
				},
				context_instance=RequestContext(request))

def iauction_sell(request, template="iauction/iauction_sell.html"):
	if request.method == "POST":
		form = AuctionProductForm(request.POST, request.FILES)
		if form.is_valid():
			product = AuctionProduct()
			product.seller = request.user
			product.name = form.cleaned_data["name"]
			product.details = form.cleaned_data["details"]
			product.start_price = form.cleaned_data["start_price"]
			product.start_time = datetime.now()
			end_date = form.cleaned_data["end_date"]
			product.end_time = datetime(end_date.year, end_date.month, end_date.day,
				int(form.cleaned_data["end_hour"]), 0, 0, 0)
			if request.FILES.has_key("picture"):
				product.picture = request.FILES["picture"]
			product.save()
			return HttpResponseRedirect(reverse("iauction_home"))
	else:
		form = AuctionProductForm()
	return render_to_response(template, 
				{"form": form,
				},
				context_instance=RequestContext(request))

def iauction_product(request, product_id, template="iauction/iauction_product.html"):
	product = AuctionProduct.objects.get(pk=product_id)
	product.expire()
	product.update_visits()
	bids = product.auctionbid_set.order_by("-time_stamp")
	return render_to_response(template, 
				{"product": product,
				 "bids": bids,
				},
				context_instance=RequestContext(request))

def iauction_post_bid(request):
	if request.method == "POST":
		try:
			product_id = request.POST["product_id"]
			amount = int(request.POST["amount"])
			anonymous = (request.POST["anonymous"] == "true")
			product = AuctionProduct.objects.get(pk=product_id)
			if amount > request.user.egghead.bidding_credits():
				return HttpResponse("1") # Error code 1: Not enough credit
			elif amount <= product.current_price():
				return HttpResponse("2") # Error code 2: Bid less than current price
			time_stamp = datetime.now()
			if not product.status == "A" or time_stamp > product.end_time:
				product.expire()
				return HttpResponse("3") # Error code 3: Bid later than expiration time

			# All previous bids must be cleared first
			for fca in AuctionFreezeCredit.objects.filter(bid__product=product,
				ftype="F", app="A", ttype="BI", cleared=False):
				fca.unfreeze()
				if not fca.bid.bidder == request.user:
					recipients = (fca.bid.bidder, )
					current_site = Site.objects.get_current()
					# subject = "[ " + current_site.name + " ] " + "You got outbid"
					subject = u"[ %s ] %s" % (current_site.name, _("You got outbid"))
					t = loader.get_template("iauction/email_outbid.txt")
					c = Context({
							"bid": fca.bid,
							"leading": amount,
							"current_site": current_site,
						})
					send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))

			bid = AuctionBid(product=product, bidder=request.user, amount=amount,
					time_stamp=time_stamp, anonymous=anonymous, win=False)
			bid.save()
			fca = AuctionFreezeCredit(time_stamp=time_stamp, fuser=request.user, ftype="F",
				app="A", ttype="BI", amount=amount, cleared=False, bid=bid)
			fca.save()
			return HttpResponse("0")
		except Exception, e:
			alogger.warning(e)

def iauction_post_withdraw(request):
	if request.method == "POST":
		product_id = request.POST["product_id"]
		product = AuctionProduct.objects.get(pk=product_id)
		if product.seller.id == request.user.id:
			if product.is_withdrawable():
				product.status = "W"
				product.save()
				return HttpResponse("0")
			else:
				return HttpResponse("1")
		else:
			return HttpResponse("2")

def iauction_post_confirm_delivery(request):
	if request.method == "POST":
		product_id = request.POST["product_id"]
		product = AuctionProduct.objects.get(pk=product_id)
		if product.seller.id == request.user.id:
			if product.status == "P":
				deal = product.deal()
				deal.cleared_by_seller = True
				deal.save()
				deal.finalize()
				return HttpResponse("0")
			else:
				return HttpResponse("1")
		else:
			return HttpResponse("2")

def iauction_post_confirm_receipt(request):
	if request.method == "POST":
		product_id = request.POST["product_id"]
		product = AuctionProduct.objects.get(pk=product_id)
		if product.status == "P":
			deal = product.deal()
			if deal.bid.bidder.id == request.user.id:
				deal.cleared_by_winner = True
				deal.save()
				deal.finalize()
				return HttpResponse("0")
			else:
				return HttpResponse("2")
		else:
			return HttpResponse("1")
