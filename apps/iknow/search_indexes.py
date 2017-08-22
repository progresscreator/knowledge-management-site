from haystack import indexes, site
from iknow.models import Question

class QuestionIndex(indexes.SearchIndex):
	text = indexes.CharField(document=True, use_template=True)
	time_stamp = indexes.DateTimeField(model_attr="time_stamp")
	index_pk = indexes.IntegerField(model_attr="id")

	def get_queryset(self):
		return Question.objects.all()

site.register(Question, QuestionIndex)
