# Create your views here.
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
from django.core import serializers
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
	from django.core.mail import send_mail

if "notification" in settings.INSTALLED_APPS:
	from notification import models as notification
else: 
	notification = None

from core.models import Settings
from core.forms import SettingsForm, FeatureForm
from core.utils import parse_phone_number, verified_emails
from iknow.models import Question, QuestionTag
from inews.models import AnnouncePost, NewsTag
from idoc.models import IDocument
# Python libraries
import os
import logging
import simplejson
from datetime import datetime
from datetime import timedelta

klogger = logging.getLogger("pwe.core")

@login_required
def barter_settings(request, template="core/barter_settings.html"):
	settings, created = Settings.objects.get_or_create(user=request.user)
	errors = [] 
	if request.method == "POST":
		form = SettingsForm(request.POST, instance=settings)
		form.is_valid()
		checked = True
		if form.cleaned_data["new_q_notification_txt"] and \
				not parse_phone_number(form.cleaned_data["mobile"]):
			checked = False
			errors.append(_("A correct mobile phone number is required if 'iKnow SMS' is enabled"))
		if form.cleaned_data["mobile"].strip() != "" and not parse_phone_number(form.cleaned_data["mobile"]):
			checked = False
			errors.append(_("The phone number you input is not recognized"))
			
		if form.is_valid() and checked:
			form.save()
			
			if form.cleaned_data["mobile"].strip() != "" and parse_phone_number(form.cleaned_data["mobile"]):
				settings.mobile = parse_phone_number(settings.mobile)
				settings.save()
			return HttpResponseRedirect(reverse("egghead_detail", args=[request.user.username]))
	else:
		form = SettingsForm(instance=settings)
	return render_to_response(template, 
				{"form": form,
				 "errors": errors,
				},
				context_instance=RequestContext(request))

@login_required
def feature_edit(request, feature_id=-1, template="core/feature_form.html"):
	pass

@login_required
def feature_add(request, template="core/feature_form.html"):
	if request.method == "POST":
		form = FeatureForm(request.POST)
		if form.is_valid():
			new_feature = form.save(commit=False)
			new_feature.committer = request.user
			new_feature.creation_date = datetime.today()
			new_feature.save()

			try:
				recipients = User.objects.filter(settings__new_feature_email=True)
				current_site = Site.objects.get_current()
				subject = "[ " + current_site.name + " ] "
				if new_feature.type == "B":
					subject = _("[ %(site_name)s ] Bug fixed") % {"site_name": current_site.name}
				elif new_feature.type == "F":
					subject = _("[ %(site_name)s ] A new feature is available") % {"site_name": current_site.name}
				t = loader.get_template("core/new_feature.txt")
				c = Context({
						"feature": new_feature,
						"current_site": current_site,
					})
				message = t.render(c)
				from_email = settings.DEFAULT_FROM_EMAIL
				send_mail(subject, message, from_email, verified_emails(recipients))
			except Exception, e:
				klogger.info(e)
			
			return HttpResponseRedirect(reverse("what_next"))
	else:
		form = FeatureForm()
	return render_to_response(template, 
				{"form": form,
				 "type": "add",
				},
				context_instance=RequestContext(request))

@login_required
def core_tag_experts(request, tag_id=-1, template="core/core_tag_experts.html"):
	tag = QuestionTag.objects.get(pk=tag_id)
	experts = {}
	for question in Question.objects.filter(tags__icontains=tag):
		if question.asker not in experts:
			experts[question.asker] = 1
		else:
			experts[question.asker] = experts[question.asker] + 1
		for answer in question.answer_set.all():
			if answer.answerer not in experts:
				experts[answer.answerer] = 1
			else:
				experts[answer.answerer] = experts[answer.answerer] + 1
	for doc in IDocument.objects.filter(tags__icontains=tag):
		if doc.creator not in experts:
			experts[doc.creator] = 1
		else:
			experts[doc.creator] = experts[doc.creator] + 1
	people = sorted(experts, key=experts.__getitem__, reverse=True)
	# TODO
	return render_to_response(template, 
				{"people": people,
				 "tag": tag,
				},
				context_instance=RequestContext(request))

@login_required
def core_tag_experts_news(request, tag_id=-1, template="core/core_tag_experts.html"):
	tag = NewsTag.objects.get(pk=tag_id)
	experts = {}
	for post in AnnouncePost.objects.filter(tags__icontains=tag):
		if post.creator not in experts:
			experts[post.creator] = 1
		else:
			experts[post.creator] = experts[post.creator] + 1
	for doc in IDocument.objects.filter(tags__icontains=tag):
		if doc.creator not in experts:
			experts[doc.creator] = 1
		else:
			experts[doc.creator] = experts[doc.creator] + 1
	people = sorted(experts, key=experts.__getitem__, reverse=True)
	# TODO
	return render_to_response(template, 
				{"people": people,
				 "tag": tag,
				},
				context_instance=RequestContext(request))

@login_required
def barter_json_tags(request):
	try:
		term = request.GET["term"]
		tags = [tag.name for tag in 
			QuestionTag.objects.filter(name__icontains=term).order_by("count")]
		json_string = simplejson.dumps(tags)
		return HttpResponse(json_string)
	except Exception, e:
		klogger.warning(e)
		
@login_required
def barter_json_users(request):
	try:
		term = request.GET["term"]
		users = User.objects.filter(Q(username__icontains=term)|Q(first_name__icontains=term)|Q(last_name__icontains=term))
		user_strings = list()
		for user in users:
			user_strings.append("%s %s (%s)" % (user.first_name, user.last_name, user.username))
		json_string = simplejson.dumps(user_strings)
		return HttpResponse(json_string)
	except Exception, e:
		klogger.warning(e)
		
