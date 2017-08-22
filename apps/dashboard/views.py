from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Max, Min, Avg
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat

from django.conf import settings
from knowledge_web import gviz_api
from egghead.models import get_egghead_from_user, EggHead
from worldbank.models import Transaction
from iknow.models import QuestionTag, Question, Answer
from inews.models import AnnouncePost, NewsTag
from dashboard.utils import get_icon_url, get_json_network, filter_QS_by_date

# Python libraries
import os, logging, random
from datetime import datetime, date
from datetime import timedelta
from operator import itemgetter
import math
import simplejson
import numpy

dblogger = logging.getLogger("pwe.dashboard")

@login_required
def db_home(request, username, template="dashboard/db_home.html"):
	duser = User.objects.get(username=username)
	egghead = get_egghead_from_user(duser)
	total_user = EggHead.objects.count()
	max_wealth = EggHead.objects.aggregate(max_wealth=Max("wealth_notes"))["max_wealth"]
	return render_to_response(template, 
				{"duser": duser,
				 "max_wealth": max_wealth,
				 "total_user": total_user,
				 "egghead": egghead,},
				context_instance=RequestContext(request))

@login_required
def db_tags(request, template="dashboard/db_tags.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))

def db_expertise(request, template="dashboard/db_expertise.html"):
	max_wealth = EggHead.objects.aggregate(max_wealth=Max("wealth_notes"))["max_wealth"]
	min_wealth = EggHead.objects.aggregate(min_wealth=Min("wealth_notes"))["min_wealth"]
	return render_to_response(template, 
				{"max_wealth": max_wealth,
				 "min_wealth": min_wealth,
				},
				context_instance=RequestContext(request))

def db_expertise_slab_serif(request):
	return db_expertise(request, "dashboard/db_expertise_slab_serif.html")

def db_expertise_verdana(request):
	return db_expertise(request, "dashboard/db_expertise_verdana.html")

def db_expertise_arial(request):
	return db_expertise(request, "dashboard/db_expertise_arial.html")

def db_expertise_alter_color(request):
	return db_expertise(request, "dashboard/db_expertise_alter_color.html")

def db_social(request, username, template="dashboard/db_social.html"):
	central_user = User.objects.get(username=username)
	my_icon_url = get_icon_url(central_user, 50)
	json_network = get_json_network(central_user)
	max_wealth = EggHead.objects.aggregate(max_wealth=Max("wealth_notes"))["max_wealth"]
	min_wealth = EggHead.objects.aggregate(min_wealth=Min("wealth_notes"))["min_wealth"]
	return render_to_response(template, 
				{"my_icon_url": my_icon_url,
				 "json_network": json_network,
				 "cuser": central_user,
				 "max_wealth": max_wealth,
				 "min_wealth": min_wealth,
				},
				context_instance=RequestContext(request))
def db_social_slab_serif(request, username):
	return db_social(request, username, "dashboard/db_social_slab_serif.html")

def db_social_verdana(request, username):
	return db_social(request, username, "dashboard/db_social_verdana.html")

def db_social_arial(request, username):
	return db_social(request, username, "dashboard/db_social_arial.html")

def db_social_alter_color(request, username):
	return db_social(request, username, "dashboard/db_social_alter_color.html")

def db_social_json_network(request, username):
	central_user = User.objects.get(username=username)
	json_network = get_json_network(central_user)
	return HttpResponse(json_network)
	
def db_json_expertise(request):
	tag_list = list()
	user_list = list()
	question_list = list()
	tags = QuestionTag.objects.order_by("-count")[:200]

	questions_all = list()
	eggheads_all = list()
	tags_all = [tag for tag in tags if Question.objects.filter(tags__icontains=tag)][:50]

	for tag in tags_all:
		# Tracking linked tags
		linked_tags = list()
		linked_tags_dict = dict()

		linked_questions = list()
		questions = Question.objects.filter(tags__icontains=tag.name)

		linked_eggheads = list()
		linked_eggheads_dict = dict()

		for question in questions:
			if tag.name in [sep.strip() for sep in question.tags.split(",")]:
				for tag_name in question.tags.split(","):
					try:
						l_tag = QuestionTag.objects.get(name__exact=tag_name.strip())
						if l_tag != tag and l_tag in tags_all:
							if l_tag.id in linked_tags_dict:
								linked_tags_dict[l_tag.id] = linked_tags_dict[l_tag.id] + 1
							else:
								linked_tags_dict[l_tag.id] = 1
					except Exception, e:
						dblogger.debug(e)				
			linked_questions.append(question.id)

			if not question in questions_all:
				questions_all.append(question)

			if not question.asker in eggheads_all:
				eggheads_all.append(question.asker)

			eid = question.asker.id
			if eid in linked_eggheads_dict:
				linked_eggheads_dict[eid] = linked_eggheads_dict[eid] + 1
			else:
				linked_eggheads_dict[eid] = 1

			for answer in question.answer_set.all():
				if not answer.answerer in eggheads_all:
					eggheads_all.append(answer.answerer)
				eid = answer.answerer.id
				if eid in linked_eggheads_dict:
					linked_eggheads_dict[eid] = linked_eggheads_dict[eid] + 1
				else:
					linked_eggheads_dict[eid] = 1
		sorted_eggheads = sorted(linked_eggheads_dict, key=linked_eggheads_dict.__getitem__, reverse=True)[:5]
		for tag_id in linked_tags_dict:
			linked_tags.append({
				"tag_id": tag_id,
				"count": linked_tags_dict[tag_id]
			})
		for eid in sorted_eggheads:
			linked_eggheads.append({
				"user_id": eid,
				"count": linked_eggheads_dict[eid]
			})

		tag_list.append({
			"tag_id": tag.id,
			"name": tag.name,
			"count": tag.count,
			"linked_questions": linked_questions,
			"linked_tags": linked_tags,
			"experts": linked_eggheads,
		})

	for user in eggheads_all:
		if user.get_full_name():
			name = user.get_full_name()
		else:
			name = user.username
		user_list.append({
			"user_id" : user.id,
			"name" : name,
			"img_url" : get_icon_url(user, 50),
			"profile_url": reverse("iknow_dashboard", kwargs={"username": user.username}),
			"wealth": user.egghead.wealth_notes,
		})
	for question in questions_all:
		question_list.append({
			"question_id": question.id,
			"title": question.question_title,
			"link": reverse("iknow_question", kwargs={"question_id": question.id})
		})
		
	data_dict = {
		"tags": tag_list,
		"eggheads": user_list,
		"questions": question_list
	}
	return HttpResponse(simplejson.dumps(data_dict))
	

@login_required
def db_global(request, template="dashboard/db_global.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))

@login_required
def vis_json_income_pie(request):
	description = {"app": ("string", "App"),
				   "income": ("number", "Income"),
				  }
	ksum = Transaction.objects.filter(app="K", dst=request.user).\
			aggregate(ksum=Sum("amount"))["ksum"]
	dsum = Transaction.objects.filter(app="D", dst=request.user).\
			aggregate(dsum=Sum("amount"))["dsum"]
	ssum = Transaction.objects.filter(app="S", dst=request.user).\
			aggregate(ssum=Sum("amount"))["ssum"]
	if not ksum: 
		ksum = 0
	if not dsum:
		dsum = 0
	if not ssum:
		ssum = 0
	data = [{"app": _("iKnow"), "income": ksum},
			{"app": _("iDoc"), "income": dsum},
			{"app": _("Subsidy"), "income": ssum}]
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("app","income"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 0 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("app","income"), req_id=0))

@login_required
def vis_json_inout_pie(request):
	description = {"flow": ("string", "Flow"),
				   "amount": ("number", "Amount"),
				  }
	isum = get_egghead_from_user(request.user).total_income()
	osum = get_egghead_from_user(request.user).total_spending()
	data = [{"flow": _("Inflow"), "amount": isum},
			{"flow": _("Outflow"), "amount": osum}]
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("flow","amount"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 1 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("flow","amount"), req_id=1))

@login_required
def vis_json_tag_cloud(request):
	description = {"label": ("string", "Label"),
				   "value": ("number", "Value"),
				   "link": ("string", "Link"),
				  }
	data = []
	tags = list(QuestionTag.objects.order_by("-count")[:100])
	
	random.shuffle(tags)
	for tag in tags:
		data.append({"label":tag.name, 
					 "value": tag.count,
					 "link": reverse("iknow_tag", kwargs={
						"tag_id": tag.id
					 })
				})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("label","value","link"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 0 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("label","value","link"), req_id=0))

def vis_json_tag_cloud_news(request):
	description = {"label": ("string", "Label"),
				   "value": ("number", "Value"),
				   "link": ("string", "Link"),
				  }
	data = []
	tags = list(NewsTag.objects.order_by("-count")[:100])
	
	random.shuffle(tags)
	for tag in tags:
		data.append({"label":tag.name, 
					 "value": tag.count,
					 "link": reverse("inews_tag", kwargs={
						"tag_id": tag.id
					 })
				})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("label","value","link"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 0 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("label","value","link"), req_id=0))

@login_required
def vis_json_tag_cloud_user(request, username):
	description = {"label": ("string", "Label"),
				   "value": ("number", "Value"),
				   "link": ("string", "Link"),
				  }
	data = []
	tag_dict = {}
	user = User.objects.get(username=username)
	for question in user.questions_asked.all():
		for tag in question.tags.split(","):
			if tag.strip():
				if tag.strip() not in tag_dict:
					tag_dict[tag.strip()] = 1
				else:
					tag_dict[tag.strip()] = tag_dict[tag.strip()] + 1
	for answer in user.answers_answered.all():
		for tag in answer.question.tags.split(","):
			if tag.strip():
				if tag.strip() not in tag_dict:
					tag_dict[tag.strip()] = 1
				else:
					tag_dict[tag.strip()] = tag_dict[tag.strip()] + 1
	sorted_list = sorted(tag_dict.iteritems(), key=itemgetter(1), reverse=True)[:15]
	for (k, v) in sorted_list:
		try:
			tag_obj = QuestionTag.objects.get(name=k)
			tag_link = reverse("iknow_tag", kwargs={"tag_id": tag_obj.id})
		except Exception, e:
			tag_link = reverse("iknow_dashboard", kwargs={"username": username})
		data.append({"label":k, 
					 "value": v, 
					 "link": tag_link,
				})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("label","value","link"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 0 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("label","value","link"), req_id=0))

@login_required
def vis_json_qa_vis(request):
	description = {"date": ("date", "Date"),
				   "questions": ("number", "Questions"),
				   "title1": ("string", "Title1"),
				   "text1": ("string", "Text1"),
				   "answers": ("number", "Answers"),
				   "title2": ("string", "Title2"),
				   "text2": ("string", "Text2"),
				  }
	adate = date.today()
	min_dt = Question.objects.aggregate(min_datetime=Min("time_stamp"))["min_datetime"]
	min_date = min_dt.date()
	data = []
	for k in xrange(365):
		# dblogger.debug("Date: %s" % str(adate))
		qcount = Question.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day).count()
		acount = Answer.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day).count()
		# dblogger.debug("Questions: %d" % qcount)
		# dblogger.debug("Answers: %d" % acount)
		if qcount > 0 or acount > 0:
			data.append({"date": adate,
						 "questions": qcount,
						 "answers": acount
						})

		adate = adate - timedelta(days=1)
		if adate < min_date:
			break;
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","questions","title1","text1","answers","title2"
			,"text2"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 0 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","questions","title1","text1","answers","title2"
			,"text2"), req_id=0))

@login_required
def vis_json_qa_price_vis(request):
	description = {"date": ("string", _("Date")),
				   "qprice": ("number", _("Average price of questions")),
				   "aprice": ("number", _("Average awards an answer receives")),
				  }
	adate = date.today()
	min_dt = Question.objects.aggregate(min_datetime=Min("time_stamp"))["min_datetime"]
	min_date = min_dt.date()
	data = []
	for k in xrange(365):
		# dblogger.debug("Date: %s" % str(adate))
		qprice = Question.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day).aggregate(qprice=Avg("points_offered"))["qprice"]
		aprice = Answer.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day).aggregate(aprice=Avg("points_received"))["aprice"]
		if not qprice: qprice = 0
		if not aprice: aprice = 0
		#  dblogger.debug("Questions: %.2f" % qprice)
		# dblogger.debug("Answers: %.2f" % aprice)

		data.append({"date": adate.strftime("%m-%d"),
					 "qprice": qprice,
					 "aprice": aprice
					})

		adate = adate - timedelta(days=1)
		if adate < min_date:
			break;
	data.reverse()
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","qprice", "aprice"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 1 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","qprice","aprice"), req_id=1))

@login_required
def vis_json_transactions_vis(request):
	description = {"date": ("date", "Date"),
				   "tcount": ("number", _("Number of transactions")),
				   "title1": ("string", "Title1"),
				   "text1": ("string", "Text1"),
				   "tamount": ("number", _("Transaction amount (x10)")),
				   "title2": ("string", "Title2"),
				   "text2": ("string", "Text2"),
				  }
	adate = date.today()
	min_dt = Question.objects.aggregate(min_datetime=Min("time_stamp"))["min_datetime"]
	min_date = min_dt.date()
	data = []
	for k in xrange(365):
		# dblogger.debug("Date: %s" % str(adate))
		tcount = Transaction.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day).count()
		tamount = Transaction.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day).aggregate(tamount=Sum("amount"))["tamount"]
		if not tamount: tamount = 0
		data.append({"date": adate,
					 "tcount": tcount,
					 "tamount": tamount / 10
					})

		adate = adate - timedelta(days=1)
		if adate < min_date:
			break;
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","tcount","title1","text1","tamount","title2"
			,"text2"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 2 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","tcount","title1","text1","tamount","title2"
			,"text2"), req_id=2))

@login_required
def vis_json_answer_rating(request, username):
	description = {"rating": ("string", _("Rating")),
				   "acount": ("number", _("Answers")),
				  }
	auser = User.objects.get(username=username)
	
	data = []
	for k in xrange(5):
		acount = Answer.objects.filter(answerer=auser, rating_by_asker=(k+1)).count()
		data.append({"rating": k + 1,
					 "acount": acount})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("rating","acount"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 3 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("rating","acount"), req_id=3))

@login_required
def vis_json_answer_thumbs(request, username):
	description = {"thumbs": ("string", _("Thumbs")),
				   "acount": ("number", _("Answers")),
				  }
	auser = User.objects.get(username=username)
	data = list()
	tmax = Answer.objects.filter(answerer=auser).aggregate(tmax=Max("thumbs"))["tmax"]
	acount = Answer.objects.filter(answerer=auser, thumbs__lt=0).count()
	if acount > 0:
		data.append({"thumbs": "<0", "acount": acount})
	acount = Answer.objects.filter(answerer=auser, thumbs=0).count()
	data.append({"thumbs": "0", "acount": acount})
	if tmax > 0:
		bin = math.ceil(2.0 / 9.0 * tmax)
		for k in xrange(5):
			if k < 4:
				acount = Answer.objects.filter(answerer=auser, 
					thumbs__range=(k*bin+1, (k+1)*bin)).count()
				if bin == 1:
					label = "%d" % ((k + 1) * bin)
				else:
					label = "%d~%d" % (k * bin, (k + 1) * bin)
				data.append({"thumbs": label, "acount": acount})
			else:
				acount = Answer.objects.filter(answerer=auser, 
					thumbs__gt=(k+1)*bin).count()
				label = ">%d" % ((k + 1) * bin)
				data.append({"thumbs": label, "acount": acount})
	else:
		data.append({"thumbs": ">0", "acount": 0})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("thumbs","acount"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 3 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("thumbs","acount"), req_id=4))

@login_required
def vis_json_answer_award(request, username):
	description = {"award": ("string", _("Award")),
				   "acount": ("number", _("Answers")),
				  }
	auser = User.objects.get(username=username)
	data = list()
	acount = Answer.objects.filter(answerer=auser, points_received=0).count()
	data.append({"award": "0", "acount": acount})
	interval = (0, 25, 50, 100, 200, 500)
	for k in xrange(len(interval)):
		if k < len(interval) - 1:
			acount = Answer.objects.filter(answerer=auser, 
				points_received__range=(interval[k]+1, interval[k+1])).count()
			label = "%d~%d" % (interval[k], interval[k+1])
			data.append({"award": label, "acount": acount})
		else:
			acount = Answer.objects.filter(answerer=auser, 
				points_received__gt=interval[k]).count()
			label = ">%d" % (interval[k])
			data.append({"award": label, "acount": acount})
			
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("award","acount"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 3 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("award","acount"), req_id=5))

@login_required
def vis_json_time_series(request, username):
	description = {"date": ("date", "Date"),
				   "questions": ("number", _("Questions")),
				   "title1": ("string", "Title1"),
				   "text1": ("string", "Text1"),
				   "answers": ("number", _("Answers")),
				   "title2": ("string", "Title2"),
				   "text2": ("string", "Text2"),
				   "income": ("number", _("Income")),
				   "title3": ("string", "Title3"),
				   "text3": ("string", "Text3"),
				   "spending": ("number", _("Spending")),
				   "title4": ("string", "Title4"),
				   "text4": ("string", "Text4"),
				  }
	duser = User.objects.get(username=username)
	iter_date = duser.date_joined.date()
	data = []
	while iter_date <= date.today():
		# dblogger.debug("Date: %s" % str(iter_date))
		qcount = filter_QS_by_date(Question, iter_date).filter(asker=duser).count()
		acount = filter_QS_by_date(Answer, iter_date).filter(answerer=duser).count()
		inflow = filter_QS_by_date(Transaction, iter_date).filter(dst=duser).\
					aggregate(isum=Sum("amount"))["isum"]
		if not inflow: inflow = 0
		outflow = filter_QS_by_date(Transaction, iter_date).filter(src=duser).\
					aggregate(osum=Sum("amount"))["osum"]
		if not outflow: outflow = 0

		data.append({"date": iter_date,
					 "questions": qcount,
					 "answers": acount,
					 "income": inflow,
					 "spending": outflow,
					})

		iter_date += timedelta(days=1)
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date",
				"questions","title1","text1",
				"answers","title2", "text2",
				"income", "title3", "text3",
				"spending", "title4", "text4",
			), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 6 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("date","questions","title1","text1","answers","title2"
			,"text2"), req_id=6))

@login_required
def vis_json_dist_wealth(request):
	description = {"wealth": ("string", _("Wealth")),
				   "acount": ("number", _("Users")),
				  }
	data = list()
	wealth_values = EggHead.objects.filter(wealth_notes__gte=0).values_list("wealth_notes", flat=True)
	(n, bins) = numpy.histogram(wealth_values, bins=15, normed=False)
	for k in xrange(len(n)):
		data.append({"wealth": "%d" % (int(bins[k]) / 10 * 10), "acount": n[k]})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("wealth","acount"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 3 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("wealth","acount"), req_id=3))

@login_required
def vis_json_dist_earnings(request):
	description = {"earning": ("string", _("Earning")),
				   "acount": ("number", _("Users")),
				  }
	data = list()
	earning_values = EggHead.objects.values_list("earning_total", flat=True)
	(n, bins) = numpy.histogram(earning_values, bins=15, normed=False)
	for k in xrange(len(n)):
		data.append({"earning": "%d" % (int(bins[k]) / 10 * 10), "acount": n[k]})
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("earning","acount"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 4 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("earning","acount"), req_id=4))

@login_required
def vis_json_market_pie(request):
	description = {"market": ("string", "Market"),
				   "transaction": ("number", "Transaction"),
				  }
	iknow_types = ["QA", "TI", "FO", "TU", "AC", "KQC", "KFQ", "AL"]
	ksum = Transaction.objects.filter(ttype__in=iknow_types).\
			aggregate(ksum=Sum("amount"))["ksum"]
	idoc_types = ["DUD", "DDD"]
	dsum = Transaction.objects.filter(ttype__in=idoc_types).\
			aggregate(dsum=Sum("amount"))["dsum"]
	idea_types = ["ITU", "ITC", "IRT", "IIC", "ITI"]
	isum = Transaction.objects.filter(ttype__in=idea_types).\
			aggregate(isum=Sum("amount"))["isum"]
	inews_types = ["NVU", "NVN"]
	nsum = Transaction.objects.filter(ttype__in=inews_types).\
			aggregate(nsum=Sum("amount"))["nsum"]
	idesign_types = ["DI"]
	esum = Transaction.objects.filter(ttype__in=idesign_types).\
			aggregate(esum=Sum("amount"))["esum"]
	subsidy_types = ["LI",]
	ssum = Transaction.objects.filter(ttype__in=subsidy_types).\
			aggregate(ssum=Sum("amount"))["ssum"]

	if not ksum: ksum = 0
	if not dsum: dsum = 0
	if not isum: isum = 0
	if not ssum: ssum = 0
	if not nsum: nsum = 0
	if not esum: esum = 0

	data = [{"market": _("iKnow"), "transaction": ksum},
			{"market": _("iDoc"), "transaction": dsum},
			{"market": _("iDea"), "transaction": isum},
			{"market": _("iNews"), "transaction": nsum},
			{"market": _("iDesign"), "transaction": esum},
			{"market": _("Subsidy"), "transaction": ssum}]
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("market","transaction"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 5 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("market","transaction"), req_id=5))

def get_type_trans_amount(ttype):
	a = Transaction.objects.filter(ttype=ttype).aggregate(asum=Sum("amount"))["asum"]
	if not a: a = 0
	return a


@login_required
def vis_json_type_pie(request):
	description = {"type": ("string", "Type"),
				   "transaction": ("number", "Transaction"),
				  }
	data = [{"type": _("Q&A"), "transaction": get_type_trans_amount("QA")},
			{"type": _("Q&A Tipping"), "transaction": get_type_trans_amount("TI")},
			{"type": _("Q&A Thumbing"), "transaction": get_type_trans_amount("TU")},
			{"type": _("Q&A Comment Answers"), "transaction": get_type_trans_amount("AC")},
			{"type": _("Q&A Comment Questions"), "transaction": get_type_trans_amount("KQC")},
			{"type": _("Q&A First Question"), "transaction": get_type_trans_amount("KFQ")},
			{"type": _("Q&A Points allocation"), "transaction": get_type_trans_amount("AL")},
			{"type": _("iDoc Upload a doc"), "transaction": get_type_trans_amount("DUD")},
			{"type": _("iDoc Download a doc"), "transaction": get_type_trans_amount("DDD")},
			{"type": _("iNews Post news"), "transaction": get_type_trans_amount("NVN")},
			{"type": _("iNews Vote on news"), "transaction": get_type_trans_amount("NVU")},
			{"type": _("iDesgin new idea"), "transaction": get_type_trans_amount("DI")},
			{"type": _("iDea thumbing"), "transaction": get_type_trans_amount("ITU")},
			{"type": _("iDea rating"), "transaction": get_type_trans_amount("IRT")},
			{"type": _("Logging in"), "transaction": get_type_trans_amount("LI")},
			]
	data_table = gviz_api.DataTable(description)
	data_table.LoadData(data)
	try:
		rid = int(request.GET["tqx"].split(":")[1].strip())
		# dblogger.debug("reqId is acquired from GET data: %d" % rid)
		return HttpResponse(data_table.ToJSonResponse(columns_order=("type","transaction"), req_id=rid))
	except Exception, e:
		dblogger.debug(e)
		dblogger.debug("reqId is not found in GET, use 5 instead")
		return HttpResponse(data_table.ToJSonResponse(columns_order=("type","transaction"), req_id=5))
