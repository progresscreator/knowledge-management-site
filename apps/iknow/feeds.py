from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from iknow.models import Question

class QuestionFeedAll(Feed):
	title = "Latest iknow questions"
	link = "/iknow/questions/"
	description = "Latest iknow questions"

	title_template = "iknow/feeds/title.html"
	description_template = "iknow/feeds/description.html"

	def items(self):
		return Question.objects.filter(status__in=["A", "E"]).order_by("-time_stamp")[:10]

class QuestionFeedRewarding(Feed):
	title = "Latest iknow questions"
	link = "/iknow/questions/"
	description = "Latest iknow questions"
	
	title_template = "iknow/feeds/title.html"
	description_template = "iknow/feeds/description.html"

	def items(self):
		questions = Question.objects.filter(status__in=["A", "E"], points_offered__gte=1)\
			.order_by("-points_offered")
		return questions[:10]
