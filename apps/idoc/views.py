# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat

from idoc.forms import IDocumentForm, IDocRequestForm
# from idoc.models import Document, DownloadHistory, DocumentRating
from idoc.models import IDocument, IDocRating, IDocDownload, IDocTransaction, IDocRequest
from idoc.models import IDocFreezeCredit

from iknow.models import QuestionTag
from inews.models import NewsTag
from iknow import utils
from tribes.models import Tribe
from egghead.models import get_egghead_from_user, EggHead
from worldbank.models import Transaction, FreezeCredit
from mysearch.utils import search_documents

# Python libraries
import os
from datetime import datetime
from datetime import timedelta
import logging

dlogger = logging.getLogger("pwe.idoc")

@login_required
def idoc_home(request, template="idoc/idoc_home.html"):
	if request.method == "POST":
		pass		
	documents = IDocument.objects.order_by("-time_stamp")[:40]
	egghead = get_egghead_from_user(request.user)
	top_eggheads = EggHead.objects.order_by("-wealth_notes")[:10]
	top_eggheads_earning = EggHead.objects.order_by("-earning_total")[:10]
	top_tags = QuestionTag.objects.order_by("-count")[:10]
	tribes = Tribe.objects.filter(members=request.user)
	return render_to_response(template, 
				{"docs": documents,
				 "egghead": egghead,
				 "top_eggheads": top_eggheads,
				 "top_eggheads_earning": top_eggheads_earning, 
				 "top_tags": top_tags,
				 "tribes": tribes,
				},
				context_instance=RequestContext(request))

@login_required
def idoc_edit(request, doc_id, template="idoc/idoc_edit.html"):
	doc = IDocument.objects.get(pk=doc_id)
	if request.method == "POST":
		form = IDocumentForm(request.POST, request.FILES, instance=doc)
		if form.is_valid():
			idoc = form.save(commit=False)
			idoc.save()
			return HttpResponseRedirect(doc.get_absolute_url())
	else:
		form = IDocumentForm(instance=doc)
	return render_to_response(template, 
				{
					"doc": doc,
					"form": form,
				},
				context_instance=RequestContext(request))

@login_required
def idoc_request(request, template="idoc/idoc_request.html"):
	if request.method == "POST":
		form = IDocRequestForm(request.POST)
		if form.is_valid():
			docrequest = form.save(commit=False)
			docrequest.creator = request.user
			docrequest.time_stamp = datetime.now()
			docrequest.mp_code = "DR"
			end_date = form.cleaned_data["end_date"]
			docrequest.points_expiration = datetime(end_date.year, end_date.month, end_date.day,
				int(form.cleaned_data["end_hour"]), 0, 0, 0)
			docrequest.save()
			fc = IDocFreezeCredit(
					time_stamp = datetime.now(),
					fuser = request.user,
					ftype = "F",
					app = "O",
					ttype = "DRD",
					amount = docrequest.points_offered,
					cleared = False,
					idocrequest = docrequest
				)
			fc.save()
			return HttpResponseRedirect(reverse("idoc_home"))
	else:
		form = IDocRequestForm()
	return render_to_response(template, 
				{
					"form": form,
				},
				context_instance=RequestContext(request))

@login_required
def idoc_upload(request, template="idoc/idoc_upload.html"):
	if request.method == "POST":
		try:
			form = IDocumentForm(request.POST, request.FILES)
		except IOError, e:
			dlogger.warning("idoc_upload reading request.POST FILES: %s" % e)
			return HttpResponseServerError
		if form.is_valid():
			idoc = form.save(commit=False)
			idoc.creator = request.user
			idoc.time_stamp = datetime.now()
			idoc.mp_code = "DO"
			idoc.save()
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
				idoc.tags = ", ".join(cleaned_tags)
			idoc.save()
			transaction = IDocTransaction(
							time_stamp = datetime.now(),
							flow_type = "B",
							dst = request.user,
							app = "D",
							ttype = "DUD",
							amount = 5,
							idocument = idoc)
			transaction.save()
			transaction.execute()
			return HttpResponseRedirect(reverse("idoc_home"))
	else:
		form = IDocumentForm()
	return render_to_response(template, 
				{
					"form": form,
				},
				context_instance=RequestContext(request))


#@login_required
#def idoc_share(request, template="idoc/idoc_share.html"):
#	egghead = get_egghead_from_user(request.user)
#	tribes = request.user.tribes.all()
#	if request.method == "POST":
#		form = DocumentForm(request.POST, request.FILES)
#		if form.is_valid():
#			doc = form.save(commit=False)
#			doc.owner = request.user
#			doc.creation_time = datetime.now()
#
#			cleaned_tags = []
#			for tag in doc.tags.split(","):
#				cleaned_tag = utils.clean_tag(tag)
#				if cleaned_tag:
#					cleaned_tags.append(cleaned_tag)
#					tag_obj, created = QuestionTag.objects.get_or_create(name=cleaned_tag)
#					if not created: 
#						tag_obj.update_count()
#			if cleaned_tags:
#				doc.tags = ", ".join(cleaned_tags)
#			doc.save()
#			for key in request.POST:
#				if key.startswith("tribeshare"):
#					tribe = Tribe.objects.get(pk=key.split("_")[1])
#					doc.to_groups.add(tribe)
#				if key.startswith("tribeemail"):
#					tribe = Tribe.objects.get(pk=key.split("_")[1])
#
#			transaction = Transaction(time_stamp=datetime.now(),
#							flow_type="B",
#							dst=request.user,
#							app="D",
#							ttype="DU",
#							amount=5,
#							document=doc)
#			transaction.save()
#			transaction.execute()
#			return HttpResponseRedirect(reverse("idoc_home"))
#	else:
#		form = DocumentForm()
#	return render_to_response(template, 
#				{"form": form,
#				 "tribes": tribes,
#				},
#				context_instance=RequestContext(request))

@login_required
def idoc_docs(request, template="idoc/idoc_docs.html"):
	documents = IDocument.objects.order_by("-time_stamp")
	return render_to_response(template, 
				{"docs": documents,},
				context_instance=RequestContext(request))

@login_required
def idoc_doc(request, doc_id, template="idoc/idoc_doc.html"):
	# doc = IDocument.objects.get(pk=doc_id)
	doc = get_object_or_404(IDocument, pk=doc_id)
	doc.update_visits()
	try:
		obj = IDocRating.objects.get(document=doc, rater=request.user)
		rating_msg = _("You rated the document with %(rating)d stars on %(date)s. You can always update your rating.") % {
			"rating": obj.rating,
			"date": obj.time_string_date()
		}
	except Exception, e:
		rating_msg = _("You have never rated this document. Why not provide one?")
	if doc.tags:
		results = search_documents(doc.tags)
	else:
		results = search_documents(doc.title)
	# results = results.exclude(index_pk=doc.id)[:10]
	downloads = doc.idocdownload_set.order_by("-time_stamp")[:12]
	ratings = doc.idocrating_set.order_by("-time_stamp")[:12]
	redownload = False
	if request.user == doc.creator:
		downloadable = True
	else:
		if IDocDownload.objects.filter(downloader=request.user, document=doc):
			downloadable = True
			redownload = True
		else:
			downloadable = doc.points_needed <= request.user.egghead.available_credits()
	return render_to_response(template, 
				{
					"doc": doc,
					"results": results,
					"rating_msg": rating_msg,
					"downloads": downloads,
					"ratings": ratings,
					"downloadable": downloadable,
					"redownload" : redownload,
				},	
				context_instance=RequestContext(request))

@login_required
def idoc_ajax_download(request):
	if request.method == "POST":
		try:
			did = request.POST["id"]
			doc = IDocument.objects.get(pk=did)
			if request.user == doc.creator: return HttpResponse("8")
			if IDocDownload.objects.filter(downloader=request.user, document=doc):
				charged = 0
			else:
				charged = doc.points_needed
				doc.update_downloads()
				if charged > 0:
					transaction = IDocTransaction(
									time_stamp = datetime.now(),
									flow_type = "I",
									src = request.user,
									dst = doc.creator,
									app = "D",
									ttype = "DDD",
									amount = charged,
									idocument = doc)
					transaction.save()
					transaction.execute()
			his = IDocDownload(downloader=request.user, document=doc,
				time_stamp=datetime.now(), fee=charged)
			his.save()
			return HttpResponse("0")
		except Exception, e:
			print e
			return HttpResponse("1")

	else:
		dlogger.error("idoc_ajax_download received a non-POST request")

@login_required
def idoc_ajax_tribe_docs(request, tribe_id, 
				template="idoc/idoc_ajax_tribe_docs.html"):
	tribe = Tribe.objects.get(pk=tribe_id)
	docs = IDocument.objects.filter(to_groups=tribe)
	return render_to_response(template, 
				{
					"docs": docs,
				},
				context_instance=RequestContext(request))

#saucy
@login_required
def idoc_ajax_tag_docs(request, tag_id, 
				template="idoc/idoc_ajax_tribe_docs.html"):
	tag = QuestionTag.objects.get(pk=tag_id)
	docs = IDocument.objects.filter(to_groups=tribe)
	return render_to_response(template, 
				{
					"docs": docs,
				},
				context_instance=RequestContext(request))
	

@login_required
def idoc_ajax_rating(request):
	if request.method == "POST":
		try:
			did = request.POST["id"]
			rating = int(request.POST["value"])
			doc = IDocument.objects.get(pk=did)
			obj, created = IDocRating.objects.get_or_create(document=doc, rater=request.user,
				defaults={"rating":rating, "time_stamp": datetime.now()})
			if not created:
				obj.rating = rating
				obj.time_stamp = datetime.now()
				obj.save()
			doc.update_rating()
			return HttpResponse("0")
		except Exception, e:
			dlogger.debug(e)
	else:
		dlogger.error("idoc_ajax_rating received a non-POST request")

@login_required
def idoc_ajax_docs(request, 
				qtype="all",
				tribe_id=None,	
				tag_id=None, 
				template="idoc/idoc_ajax_docs.html"):
	if qtype == "all" or qtype == "all_news" or qtype == "all_questions":
		docs = IDocument.objects.all()
		title = _("All documents")
	elif qtype == "my_favorite":
		title = _("IDocuments that you bookmarked")
		docs = None
	else:
		docs = None
	if not tribe_id:
		docs = docs.filter(to_groups=None)
	else:
		tribe = Tribe.objects.get(pk=tribe_id)
		docs = docs.filter(to_groups=tribe)
	if tag_id and qtype == "all_news":
		tag = NewsTag.objects.get(pk=tag_id)
		title = "Documents tagged with '" + tag.name + "'"
		docs = docs.filter(tags__icontains=tag.name)

	elif tag_id and qtype == "all_questions":
		tag = QuestionTag.objects.get(pk=tag_id)
		title = "Documents tagged with '" + tag.name + "'"
		docs = docs.filter(tags__icontains=tag.name)

	if not docs:
		return render_to_response(template, 
					{"objs": None,
					 "title": title,
					 "order": "time", 
					 "page": 0,
					 "total_pages": 0,
					 "qtype": qtype,
					 },
					context_instance=RequestContext(request))
	order = "time"
	page = 1
	if request.method == "POST":
		if request.POST.has_key("order"):
			order = request.POST["order"]
		if request.POST.has_key("page"):
			page = int(request.POST["page"])
	if order == "time":
		d_ordered = docs.order_by("-time_stamp")
	paginator = Paginator(d_ordered, 20)
	return render_to_response(template, 
				{"objs":paginator.page(page),
				 "title": title,
				 "order": order, 
				 "page": page,
				 "total_pages": paginator.num_pages,
				 "qtype": qtype,
				 },
				context_instance=RequestContext(request))

@login_required
def idoc_help(request, template="idoc/idoc_help.html"):

	return render_to_response(template, 
				{},
				context_instance=RequestContext(request))
