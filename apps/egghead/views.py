# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.conf import settings

from egghead.forms import EggheadForm
from egghead.models import get_egghead_from_user
from tribes.models import Tribe

# Python libraries
import os
from datetime import datetime, date
from datetime import timedelta

@login_required
def egghead_detail(request, username, template="egghead/egghead_detail.html"):
	person = User.objects.get(username=username)
	profile = person.get_profile()
	egghead = get_egghead_from_user(person)
	settings, created = Settings.objects.get_or_create(user=request.user)
	return render_to_response(template, 
				{"person": person,
				 "profile": profile,
				 "settings": settings,
				 "egghead": egghead,},
				context_instance=RequestContext(request))

@login_required
def egghead_ajax_tribe_members(request, tribe_id, 
			template="egghead/egghead_ajax_tribe_members.html"):
	tribe = Tribe.objects.get(pk=tribe_id)
	return render_to_response(template, 
				{"members": tribe.members.all(),},
				context_instance=RequestContext(request))
	
@login_required
def egghead_edit(request, template="egghead/egghead.html"):
	if request.method == "POST":
		form = EggheadForm(request.POST)
		if form.is_valid():
			request.user.first_name = form.cleaned_data["first_name"]
			request.user.last_name = form.cleaned_data["last_name"]
			request.user.email = form.cleaned_data["email"]
			request.user.save()

			egghead = get_egghead_from_user(request.user)
			egghead.gtalk = form.cleaned_data["gtalk"]
			egghead.facebook = form.cleaned_data["facebook"]
			egghead.twitter = form.cleaned_data["twitter"]

			egghead.title = form.cleaned_data["title"]
			egghead.affiliation = form.cleaned_data["affiliation"]
			egghead.program_year = form.cleaned_data["program_year"]

			egghead.expertise_tags = form.cleaned_data["expertise_tags"]
			egghead.prior_experiences = form.cleaned_data["prior_experiences"]
			egghead.geographic_interests = form.cleaned_data["geographic_interests"]
			egghead.sector_interests = form.cleaned_data["sector_interests"]
			egghead.save()

			profile = request.user.get_profile()
			profile.location = form.cleaned_data["location"]
			profile.about = form.cleaned_data["about"]
			profile.website = form.cleaned_data["website"]
			profile.save()
			return HttpResponseRedirect(reverse("egghead_detail", args=[request.user.username]))
	else:
		egghead = get_egghead_from_user(request.user)
		profile = request.user.get_profile()
		data = {
			"first_name": request.user.first_name,
			"last_name": request.user.last_name,
			"email": request.user.email,
			"gtalk": egghead.gtalk,
			"facebook": egghead.facebook,
			"twitter": egghead.twitter,
			"program_year": egghead.program_year,
			"prior_experiences": egghead.prior_experiences,
			"geographic_interests": egghead.geographic_interests,
			"sector_interests": egghead.sector_interests,
			"title": egghead.title,
			"affiliation": egghead.affiliation,
			"expertise_tags": egghead.expertise_tags,
			"location": profile.location,
			"about": profile.about,
			"website": profile.website,
		}
		form = EggheadForm(data)
	return render_to_response(template, 
				{"form": form,},
				context_instance=RequestContext(request))


from account.utils import get_default_redirect
from account.forms import SignupForm, LoginForm
def bu2010spring(request, form_class=SignupForm,
		template="egghead/bu2010spring.html", success_url=None):
	if success_url is None:
		success_url = get_default_redirect(request)
	form_checking_errors = []
	form_checking_passed = True
	if request.method == "POST":
		form = form_class(request.POST)
		course = request.POST["course"]
		cohort = request.POST["cohort"]
		if course == "None":
			form_checking_passed = False
			form_checking_errors.append("You must choose a course number")
		if cohort == "None":
			form_checking_passed = False
			form_checking_errors.append("You must select a cohort (A~D)")
		if request.POST["email"].find("@bu.edu") < 0\
			and request.POST["email"].find("mit.edu") < 0:
			form_checking_passed = False
			form_checking_errors.append("You must use a BU email address")
		if form.is_valid() and form_checking_passed:
			username, password = form.save()
			user = User.objects.get(username=username)
			descp = "Students who register with the course " + course + \
				" at Boston University, offered by Prof. Marshall Van Alstyne"
			marshall, created = User.objects.get_or_create(username="MVA")
			course_tribe, created = Tribe.objects.get_or_create(slug=course, defaults={
							"name":course,
							"creator":marshall,
							"created":datetime.now(),
							"description":descp,
						})
			course_tribe.members.add(user)

			descp = "Students in " + course + " , Cohort " + cohort
			cohort_tribe, created = Tribe.objects.get_or_create(slug=course+"_"+cohort, defaults={
							"name":course + " Corhort " + cohort,
							"creator":marshall,
							"created":datetime.now(),
							"description":descp,
						})
			cohort_tribe.members.add(user)

			if settings.ACCOUNT_EMAIL_VERIFICATION:
				return render_to_response("account/verification_sent.html", {
					"email": form.cleaned_data["email"],
				}, context_instance=RequestContext(request))
			else:
				user = authenticate(username=username, password=password)
				auth_login(request, user)
				request.user.message_set.create(
					message=_("Successfully logged in as %(username)s.") % {
					'username': user.username
				})
				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	return render_to_response(template, {
		"form": form,
		"form_errors": form_checking_errors,
	}, context_instance=RequestContext(request))

association_model = models.get_model('django_openid', 'Association')
if association_model is not None:
	from django_openid.models import UserOpenidAssociation
from core.models import Settings
from worldbank.models import Transaction
def login(request, form_class=LoginForm, template_name="account/login.html",
			success_url=None, associate_openid=False, openid_success_url=None,
			url_required=False, extra_context=None):
	if extra_context is None:
		extra_context = {}
	if success_url is None:
		# success_url = get_default_redirect(request)
		success_url = reverse("iknow_home")
	if request.method == "POST" and not url_required:
		form = form_class(request.POST)
		if form.login(request):
			if associate_openid and association_model is not None:
				for openid in request.session.get('openids', []):
					assoc, created = UserOpenidAssociation.objects.get_or_create(
						user=form.user, openid=openid.openid
					)
				success_url = openid_success_url or success_url
			# Create a setting object
			Settings.objects.get_or_create(user=form.user)
			today = date.today()
			lcount = Transaction.objects.filter(ttype="LI", dst=form.user, flow_type="B", app="S",
				time_stamp__year=today.year, time_stamp__month=today.month, time_stamp__day=today.day).count()
			if lcount == 0:
				transaction = Transaction(
					time_stamp = datetime.now(),
					flow_type = "B",
					dst = form.user,
					app = "S",
					ttype = "LI", 
					amount = 3
				)
				transaction.save()
				transaction.execute()
			return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	ctx = {
		"form": form,
		"url_required": url_required,
	}
	ctx.update(extra_context)
	return render_to_response(template_name, ctx,
		context_instance = RequestContext(request)
	)

def mit_bu_signup(request, form_class=SignupForm,
		template="egghead/mit_bu_signup.html", success_url=None):
	if success_url is None:
		success_url = get_default_redirect(request)
	form_checking_errors = []
	form_checking_passed = True
	if request.method == "POST":
		form = form_class(request.POST)
		if request.POST["email"].lower().find("@bu.edu") < 0\
			and request.POST["email"].lower().find("@mit.edu") < 0\
			and request.POST["email"].lower().find("@tulane.edu") < 0:
			form_checking_passed = False
			form_checking_errors.append(_("You must use an email address from accepted universities"))
		if form.is_valid() and form_checking_passed:
			username, password = form.save()
			user = User.objects.get(username=username)
			if settings.ACCOUNT_EMAIL_VERIFICATION:
				return render_to_response("account/verification_sent.html", {
					"email": form.cleaned_data["email"],
				}, context_instance=RequestContext(request))
			else:
				user = authenticate(username=username, password=password)
				auth_login(request, user)
				request.user.message_set.create(
					message=_("Successfully logged in as %(username)s.") % {
					'username': user.username
				})
				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	return render_to_response(template, {
		"form": form,
		"form_errors": form_checking_errors,
	}, context_instance=RequestContext(request))


def french_signup(request, form_class=SignupForm,
		template="egghead/french_signup.html", success_url=None):
	if success_url is None:
		success_url = get_default_redirect(request)
	form_checking_errors = []
	form_checking_passed = True
	if request.method == "POST":
		form = form_class(request.POST)
		if request.POST["email"].lower().find(".edu") < 0:
			form_checking_passed = False
			form_checking_errors.append(_("You must use an email address from accepted universities"))
		if form.is_valid() and form_checking_passed:
			username, password = form.save()
			user = User.objects.get(username=username)
			if settings.ACCOUNT_EMAIL_VERIFICATION:
				return render_to_response("account/verification_sent.html", {
					"email": form.cleaned_data["email"],
				}, context_instance=RequestContext(request))
			else:
				user = authenticate(username=username, password=password)
				auth_login(request, user)
				request.user.message_set.create(
					message=_("Successfully logged in as %(username)s.") % {
					'username': user.username
				})
				return HttpResponseRedirect(success_url)
	else:
		form = form_class()
	return render_to_response(template, {
		"form": form,
		"form_errors": form_checking_errors,
	}, context_instance=RequestContext(request))
