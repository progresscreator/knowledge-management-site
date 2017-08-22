from haystack import indexes, site
from idoc.models import IDocument

class DocumentIndex(indexes.SearchIndex):
	text = indexes.CharField(document=True, use_template=True)
	time_stamp = indexes.DateTimeField(model_attr="time_stamp")
	index_pk = indexes.IntegerField(model_attr="id")

	def get_queryset(self):
		return IDocument.objects.all()

site.register(IDocument, DocumentIndex)
