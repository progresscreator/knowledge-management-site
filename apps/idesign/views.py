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

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
	from django.core.mail import send_mail

from idesign.forms import DesignIdeaForm
from idesign.models import DesignIdea, DesignIdeaThumb, DesignIdeaDonate, DesignIdeaFreezeCredit
# from worldbank.models import FreezeCreditDesignIdea
from worldbank.utils import worldbank_subsidize
from egghead.models import get_egghead_from_user
from iknow import utils
from iknow.models import QuestionTag

# Python libraries
import os
import logging
from datetime import datetime
from datetime import timedelta
import simplejson

dlogger = logging.getLogger("pwe.idesign")

@login_required
def idesign_home(request, template="idesign/idesign_home.html"):
	my_ideas = DesignIdea.objects.filter(creator=request.user).order_by("-time_stamp","-thumbs")[:10]
	new_ideas = DesignIdea.objects.filter(status="A").exclude(creator=request.user).order_by("-time_stamp")[:10]
	top5_points = DesignIdea.objects.filter(status="A").order_by("-points_final")[:5]
	top5_thumbs = DesignIdea.objects.filter(status="A").order_by("-thumbs")[:5]
	return render_to_response(template, {
					"my_ideas": my_ideas,
					"new_ideas": new_ideas,
					"top5_points": top5_points,
					"top5_thumbs": top5_thumbs,
				},
				context_instance=RequestContext(request))

@login_required
def idesign_designideas(request, template="idesign/idesign_designideas.html"):
	ideas = DesignIdea.objects.order_by("-time_stamp")
	return render_to_response(template, {
					"ideas": ideas,
				},
				context_instance=RequestContext(request))

@login_required
def idesign_designidea(request, designidea_id="-1", template="idesign/idesign_designidea.html"):
	designidea = DesignIdea.objects.get(pk=designidea_id)
	thumbs = designidea.designideathumb_set.order_by("-time_stamp")
	my_donates = designidea.designideadonate_set.filter(donater=request.user)\
				.order_by("-time_stamp")
	donates = designidea.designideadonate_set.exclude(donater=request.user)\
				.order_by("-time_stamp")
	return render_to_response(template, {
					"designidea": designidea,
					"thumbs": thumbs,
					"my_donates": my_donates,
					"donates": donates,
				},
				context_instance=RequestContext(request))


@login_required
def idesign_submit(request, template="idesign/idesign_submit.html"):
	egghead = get_egghead_from_user(request.user)
	form_error = list()
	if request.method == "POST":
		form = DesignIdeaForm(request.POST)
		is_valid = True
		points_offered = request.POST.get("points_offered", 0)
		if not points_offered: points_offered = 0
		if int(points_offered) > egghead.available_credits():
			is_valid = False
			form_error.append("Offered points exceed available credits")
		if form.is_valid() and is_valid:
			designidea = form.save(commit=False)
			designidea.creator = request.user
			designidea.time_stamp = datetime.now()
			if designidea.points_offered > 0:
				designidea.points_expiration = designidea.time_stamp + timedelta(days=int(60))
			cleaned_tags = []
			for tag in designidea.tags.split(","):
				cleaned_tag = utils.clean_tag(tag)
				if cleaned_tag:
					cleaned_tags.append(cleaned_tag)
					tag_obj, created = QuestionTag.objects.get_or_create(name=cleaned_tag)
					if not created: 
						tag_obj.update_count()
			if cleaned_tags:
				designidea.tags = ", ".join(cleaned_tags)
			designidea.points_final = designidea.points_offered
			designidea.save()
			worldbank_subsidize(request.user, "DI")
			if designidea.points_offered > 0:
				freezecredit = DesignIdeaFreezeCredit(time_stamp=datetime.now(), fuser=request.user, ftype="F",
					app="D", ttype="DS", amount=designidea.points_offered, designidea=designidea, cleared=False)
				freezecredit.save()
			return HttpResponseRedirect(reverse("idesign_home"))
		else:
			form_error.append("The form itself is not valid")
	else:
		form = DesignIdeaForm()
	return render_to_response(template, 
				{"form": form,
				 "form_error": form_error,
				},
				context_instance=RequestContext(request))
@login_required
def idesign_post_thumbs(request):
	if request.method == "POST":
		try:
			di_id = request.POST["id"]		
			up_or_down = request.POST["up_or_down"]
			di = DesignIdea.objects.get(pk=di_id)
			if di.creator == request.user: return HttpResponse("2")
			thumb, created = DesignIdeaThumb.objects.get_or_create(thumber=request.user, designidea=di,
					defaults={"time_stamp": datetime.now(), "up_or_down":up_or_down})
			if created: 
				di.update_thumbs()
				return HttpResponse("0")
			else: 
				return HttpResponse("1")
		except Exception, e:
			dlogger.warning(e)
			return HttpResponse("3")

@login_required
def idesign_post_donate(request):
	if request.method == "POST":
		try:
			di_id = request.POST["id"]
			amount = int(request.POST["amount"])
			di = DesignIdea.objects.get(pk=di_id)
			if di.status == "A" and amount > 0:
				donate = DesignIdeaDonate(donater=request.user, amount=amount,
					time_stamp=datetime.now(), designidea=di)
				donate.save()
				di.update_points_final()
				###
				freezecredit = DesignIdeaFreezeCredit(time_stamp=datetime.now(), fuser=request.user, ftype="F",
					is_donate=True,
					app="D", ttype="DS", amount=amount, designidea=di, cleared=False)
				freezecredit.save()
				###
				return HttpResponse("0")
		except Exception, e:
			print e
			dlogger.warning(e)
			return HttpResponse("3")
	else:
		dlogger.warning("idesign_post_donate received a non-POST request")
