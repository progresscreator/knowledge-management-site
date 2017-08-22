# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.sites.models import Site
from datetime import datetime, timedelta
from django.utils.translation import ugettext, ugettext_lazy as _

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
	from django.core.mail import send_mail

import logging
from iknow.models import QuestionTag
from iknow import utils
from idea.models import CoolIdea, CoolIdeaThumb, CoolIdeaRequest, CoolIdeaRating, CoolIdeaFreezeCredit, CoolIdeaComment, CoolIdeaCommentThumb, CoolIdeaCommentTip, CoolIdeaTransaction
from idea.forms import CoolIdeaForm
from idea import utils as idea_utils
from core.utils import verified_emails

ilogger = logging.getLogger("pwe.idea")

@login_required
def idea_home(request, template="idea/idea_home.html"):
	new_ideas = CoolIdea.objects.order_by("-time_stamp")[:10]
	my_ideas = CoolIdea.objects.filter(creator=request.user).order_by("-time_stamp")[:5]
	col_ideas = request.user.ideas_involved.order_by("-time_stamp")[:5]
	top5_rating = CoolIdea.objects.order_by("-rating")[:5]
	top5_thumbs = CoolIdea.objects.order_by("-thumbs")[:5]
	return render_to_response(template, 
				{
					"new_ideas": new_ideas,
					"my_ideas": my_ideas,
					"col_ideas": col_ideas,
					"top5_rating": top5_rating,
					"top5_thumbs": top5_thumbs,
				},
				context_instance=RequestContext(request))

@login_required
def idea_coolidea_submit(request, template="idea/idea_coolidea_submit.html"):
	if request.method == "POST":
		form = CoolIdeaForm(request.POST, request.FILES)
		if form.is_valid():
			idea = form.save(commit=False)
			idea.creator = request.user
			idea.time_stamp = datetime.now()
			idea.mp_code = "ID"
			idea.version = "1.0"
			# Processing tags
			tags = form.cleaned_data["tags"]
			cleaned_tags = []
			for tag in tags.split(","):
				cleaned_tag = utils.clean_tag(tag)
				if cleaned_tag:
					cleaned_tags.append(cleaned_tag)
					tag_obj, created = QuestionTag.objects.get_or_create(name=cleaned_tag)
					if not created: 
						tag_obj.update_count()
			if cleaned_tags:
				idea.tags = ", ".join(cleaned_tags)
			idea.save()

#			end_date = form.cleaned_data["end_date"]
#			if idea.points_offered > 0:
#				idea.points_expiration = datetime(end_date.year, end_date.month, end_date.day,
#					int(form.cleaned_data["end_hour"]), 0, 0, 0)
#			else:
#				idea.points_expiration = idea.time_stamp + timedelta(days=7)
#			idea.save()

			# Processing collaborators
			collaborators = form.cleaned_data["internal_col"]
			for name in collaborators.split(","):
				if name.strip():
					l_ind = name.find("(")
					r_ind = name.find(")")
					if l_ind > -1 and r_ind > l_ind:
						username = name[l_ind+1:r_ind].strip()
						try:
							user = User.objects.get(username=username)
							idea.collaborators.add(user)
						except Exception, e:
							pass
			idea.save()
#			if idea.points_offered > 0:
#				freezecredit = CoolIdeaFreezeCredit(time_stamp=datetime.now(), 
#								fuser=request.user, 
#								ftype="F",
#								app="I", 
#								ttype="IRC", 
#								amount=idea.points_offered, 
#								coolidea=idea, 
#								cleared=False)
#				freezecredit.save()
			return HttpResponseRedirect(reverse("idea_coolidea", kwargs={"coolidea_id": idea.id}))
	else:
		form = CoolIdeaForm()
	return render_to_response(template, 
				{
					"form": form,
				},
				context_instance=RequestContext(request))


@login_required
def idea_coolidea(request, coolidea_id="-1", template="idea/idea_coolidea.html"):
	# coolidea = CoolIdea.objects.get(pk=coolidea_id)
	coolidea = get_object_or_404(CoolIdea, pk=coolidea_id)
	collaborators = coolidea.collaborators.all()
	thumbs = coolidea.coolideathumb_set.order_by("-time_stamp")[:15]
	ratings = coolidea.coolidearating_set.order_by("-time_stamp")[:15]
	comments = coolidea.coolideacomment_set.order_by("-time_stamp")[:15]
	try:
		obj = CoolIdeaRating.objects.get(coolidea=coolidea, rater=request.user)
		rating_msg = _("You rated the idea with <strong>" + str(obj.rating) + \
				" star(s)</strong> on " + obj.time_string_date() + \
				". You can always update your rating")
	except Exception, e:
		rating_msg = _("You have never rated this idea. Why not provide one?")
	return render_to_response(template, {
					"coolidea": coolidea,
					"collaborators": collaborators,
					"thumbs": thumbs,
					"ratings": ratings,
					"rating_msg": rating_msg,
					"comments": comments,
				},
				context_instance=RequestContext(request))

@login_required
def idea_coolideas(request, template="idea/idea_coolideas.html"):
	ideas = CoolIdea.objects.all()
	order = request.GET.get("order", "time")
	try:
		page = int(request.GET.get("page", 1))
	except Exception, e:
		page = 1
	if order == "time":
		ideas_ordered = ideas.order_by("-time_stamp")
	elif order == "rating":
		ideas_ordered = ideas.order_by("-rating")
	elif order == "thumbs":
		ideas_ordered = ideas.order_by("-thumbs")
	elif order == "user":
		ideas_ordered = ideas.order_by("creator")
	else:
		order = "time"
		ideas_ordered = ideas.order_by("-time_stamp")
	paginator = Paginator(ideas_ordered, 15)
	total_pages = paginator.num_pages
	if page < 1: page = 1
	if page > total_pages: page = total_pages
	return render_to_response(template, {
					"ideas": paginator.page(page),
					"page": page,
					"total_pages": total_pages,
					"order": order,
				},
				context_instance=RequestContext(request))

@login_required
def idea_post_thumbs(request):
	if request.method == "POST":
		try:
			idea_id = request.POST["id"]		
			up_or_down = request.POST["up_or_down"]
			idea = CoolIdea.objects.get(pk=idea_id)
			if idea.creator == request.user: return HttpResponse("2")
			thumb, created = CoolIdeaThumb.objects.get_or_create(thumber=request.user, coolidea=idea,
					defaults={"time_stamp": datetime.now(), "up_or_down":up_or_down})
			if created: 
				idea.update_thumbs()
				if idea_utils.worldbank_subsidize(request.user, "ITU", coolidea=idea) == 0:
					return HttpResponse("8")
				else:
					return HttpResponse("0")
			else: 
				return HttpResponse("1")
		except Exception, e:
			ilogger.warning("Rating error: %s" % e)
			return HttpResponse("3")

@login_required
def idea_post_rating(request):
	if request.method == "POST":
		try:
			idea_id = request.POST["id"]
			rating = int(request.POST["value"])
			coolidea = CoolIdea.objects.get(pk=idea_id)

			ilogger.error("coolidea id: %d" % coolidea.id)

			obj, created = CoolIdeaRating.objects.get_or_create(coolidea=coolidea, rater=request.user,
				defaults={"rating":rating, "time_stamp": datetime.now()})
			if not created:
				ilogger.error("coolidea rating already existed");
				obj.rating = rating
				obj.time_stamp = datetime.now()
				obj.save()
				coolidea.update_rating()
				return HttpResponse("0")
			else:
				ilogger.error("coolidea rating created");
				coolidea.update_rating()
				if coolidea.creator != request.user and idea_utils.worldbank_subsidize(request.user, "IRT", coolidea=coolidea) == 0:
					return HttpResponse("8")
				else:
					return HttpResponse("0")
		except Exception, e:
			ilogger.error(e)
			return HttpResponse("3")
	else:
		ilogger.error("idoc_ajax_rating received a non-POST request")

@login_required
def idea_post_coolidea_comment(request):
	if request.method == "POST":
		comment = request.POST["comment"]
		cleaned_comment = comment.strip(" \n\t")	
		if not cleaned_comment:
			# error code 1, the comment itself is not valid
			return HttpResponse("1")
		anony = True
		if request.POST["anonymous"] == "false":
			anony = False
		try:
			coolidea_id = request.POST["coolidea_id"]
			coolidea = CoolIdea.objects.get(pk=coolidea_id)
			cic = CoolIdeaComment(coolidea=coolidea, creator=request.user, mp_code="DC",
				time_stamp=datetime.now(), details=cleaned_comment, anonymous=anony)
			cic.save()
			recipients = set()
			if coolidea.creator != request.user:
				recipients.add(coolidea.creator)
			for comment in coolidea.coolideacomment_set.all():
				if comment.creator != request.user:
					recipients.add(comment.creator)
			if recipients:
				current_site = Site.objects.get_current()
				subject = "[ " + current_site.name + " ] " + "- CoolIdea received a comment"
				t = loader.get_template("idea/emails/coolidea_new_comment.txt")
				c = Context({
						"coolidea": coolidea,
						"current_site": current_site,
						"comment": cic,
					})
				send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))
			if CoolIdeaComment.objects.filter(coolidea=coolidea, creator=request.user).count() == 1 \
				and idea_utils.worldbank_subsidize(request.user, "IIC", coolidea) == 0:
				return HttpResponse("8")
			else:
				return HttpResponse("0")
		except Exception, e:
			ilogger.warning(e)
			return HttpResponse("2")
	else:
		ilogger.warning("idea_post_coolidea_comment received a non-POST request")

@login_required
def idea_ajax_coolidea_comments(request, coolidea_id=-1, template="idea/idea_coolidea_comments.html"):
	coolidea = CoolIdea.objects.get(pk=coolidea_id)
	comments = coolidea.coolideacomment_set.all()
	order = request.GET.get("order", "time")
	try:
		page = int(request.GET.get("page", 1))
	except Exception, e:
		page = 1
	if order == "thumbs":
		comments_ordered = comments.order_by("-thumbs")
	else:
		order = "time"
		comments_ordered = comments.order_by("-time_stamp")
	paginator = Paginator(comments_ordered, 15)
	total_pages = paginator.num_pages
	if page < 1: page = 1
	if page > total_pages: page = total_pages
	return render_to_response(template, {
					"comments": paginator.page(page),
					"page": page,
					"total_pages": total_pages,
					"order": order,
					"coolidea_id": coolidea.id,
					"comments_count": comments_ordered.count(),
				},
				context_instance=RequestContext(request))

	
@login_required
def idea_post_comment_thumbs(request):
	if request.method == "POST":
		try:
			comment_id = request.POST["comment_id"]
			up_or_down = request.POST["up_or_down"]
			comment = CoolIdeaComment.objects.get(pk=comment_id)
			if comment.creator == request.user:
				return HttpResponse("2")

			thumb, created = CoolIdeaCommentThumb.objects.get_or_create(thumber=request.user, 
					comment=comment, defaults={"time_stamp": datetime.now()})
			if created:
				thumb.up_or_down = up_or_down
				thumb.save()
				if up_or_down == "U":
					comment.thumb_up = comment.thumb_up + 1
				else:
					comment.thumb_down = comment.thumb_down + 1
				comment.save()
				comment.update_thumbs()
				if idea_utils.worldbank_subsidize(request.user, "ITC", coolidea=comment.coolidea,
					coolideacomment=comment) == 0:
					return HttpResponse("8")
				else:
					return HttpResponse("0")
			else:
				return HttpResponse("1")
		except Exception, e:
			ilogger.warning("Thumbing on coolidea comments: %s" % e)
			return HttpResponse("3")
			

@login_required
def idea_post_comment_tipping(request):
	if request.method == "POST":
		try:
			comment_id = request.POST["comment_id"]
			tip = int(request.POST["tip"])

			if tip > request.user.egghead.available_credits():
				return HttpResponse("2")

			comment = CoolIdeaComment.objects.get(pk=comment_id)
			cict = CoolIdeaCommentTip(comment=comment, tipper=request.user,
				time_stamp=datetime.now(), amount=tip)
			cict.save()
			transaction = CoolIdeaTransaction(time_stamp=cict.time_stamp,
							flow_type = "I",
							src = request.user,
							dst = comment.creator,
							app = "I",
							ttype = "ITI",
							amount = tip,
							coolidea=comment.coolidea,
							coolideacomment=comment)
			transaction.save()
			transaction.execute()

			recipients = (comment.creator, )
			current_site = Site.objects.get_current()
			subject = u"[ %s ] %s" % (current_site.name, _("Your comment received %(tip_amount)d points tipping from %(tipper_name)s") % {
					"tip_amount": cict.amount,
					"tipper_name": request.user.egghead.display_name()
				})
			t = loader.get_template("idea/emails/comment_tips_received.txt")
			c = Context({
					"comment": comment,
					"current_site": current_site,
					"tip": cict,
				})
			send_mail(subject, t.render(c), settings.DEFAULT_FROM_EMAIL, verified_emails(recipients))

			return HttpResponse("0")
		except Exception, e:
			ilogger.info(e)
			return HttpResponse("1")

@login_required
def idea_help(request, template="idea/idea_help.html"):

	return render_to_response(template, 
				{},
				context_instance=RequestContext(request))
