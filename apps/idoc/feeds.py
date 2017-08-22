from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from idoc.models import IDocument

class DocumentFeedAll(Feed):
	title = "Latest idoc documents"
	link = "/idoc/docs/"
	description = "Latest idoc documents"

	title_template = "idoc/feeds/title.html"
	description_template = "idoc/feeds/description.html"

	def items(self):
		return IDocument.objects.order_by("-time_stamp")[:10]
