from django.conf import settings
from django.core.urlresolvers import reverse
import simplejson
import random
def get_icon_url(user, size):
	avatar_set = user.avatar_set.filter(primary=True)
	if avatar_set:
		my_avatar = avatar_set[0]
		if not my_avatar.thumbnail_exists(size):
			my_avatar.create_thumbnail(size)
		icon_url = my_avatar.avatar_url(size)
	else:
		icon_name = "core/images/einstein%d.png" % random.randint(1, 4)
		icon_url = settings.STATIC_URL + icon_name
	return icon_url

def seek_egghead(network_list, user_id):
	for egghead in network_list:
		if egghead["user_id"] == user_id:
			return egghead
	return None
	
def get_json_network(user):
	network_list = list()
	for question in user.questions_asked.filter(anonymous=False):
		question_dict = {"title": question.question_title, 
			"link": reverse("iknow_question", kwargs={"question_id": question.id})}
		for answer in question.answer_set.filter(anonymous=False):
			egghead = seek_egghead(network_list, answer.answerer.id)
			if not egghead:
				network_list.append({
					"user_id" : answer.answerer.id,
					"name" : answer.display_name(),
					"icon_url" : get_icon_url(answer.answerer, 50),
					"profile_url": reverse("iknow_dashboard", kwargs={"username": answer.answerer.username}),
					"wealth": answer.answerer.egghead.wealth_notes,
					"ask_url": reverse("iknow_ask"),
					"go_url": reverse("db_social", kwargs={"username": answer.answerer.username}),
					"ans_qs" : [ question_dict ], 
					"ask_qs" : [],
				})
			else:
				egghead["ans_qs"].append(question_dict)
	for answer in user.answers_answered.filter(anonymous=False, question__anonymous=False):
		question_dict = {"title": answer.question.question_title, 
			"link": reverse("iknow_question", kwargs={"question_id": answer.question.id})}
		egghead = seek_egghead(network_list, answer.question.asker.id)
		if not egghead:
			network_list.append({
				"user_id": answer.question.asker.id,
				"name": answer.question.display_name(),
				"icon_url": get_icon_url(answer.question.asker, 50),
				"profile_url": reverse("iknow_dashboard", kwargs={"username": answer.question.asker.username}),
				"wealth": answer.question.asker.egghead.wealth_notes,
				"ask_url": reverse("iknow_ask"),
				"go_url": reverse("db_social", kwargs={"username": answer.question.asker.username}),
				"ans_qs": [],
				"ask_qs": [ question_dict ], 
			})
		else:
			egghead["ask_qs"].append(question_dict)
	return simplejson.dumps(network_list)		
		
def filter_QS_by_date(QModel, adate):
	return QModel.objects.filter(time_stamp__year=adate.year, time_stamp__month=adate.month,
			time_stamp__day=adate.day)
	
