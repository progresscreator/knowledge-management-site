from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from idoc.views import *

urlpatterns = patterns('',
    url(r'^$', idoc_home, name="idoc_home"),
	url(r'^docs/$', idoc_docs, name="idoc_docs"),
    url(r'^doc/(?P<doc_id>\d+)/$', idoc_doc, name="idoc_doc"),
    url(r'^edit/(?P<doc_id>\d+)/$', idoc_edit, name="idoc_edit"),
	url(r'^help/$', idoc_help, name="idoc_help"),
    url(r'^ajax/download/$', idoc_ajax_download, name="idoc_ajax_download"),
    url(r'^ajax/rating/$', idoc_ajax_rating, name="idoc_ajax_rating"),
    url(r'^ajax/tribe/docs/(?P<tribe_id>\d+)/$', idoc_ajax_tribe_docs, name="idoc_ajax_tribe_docs"),
    url(r'^ajax/docs/tags/(?P<qtype>\w+)/(?P<tag_id>\d+)/$', idoc_ajax_docs, name="idoc_ajax_tag_docs"),

	# urls for the new document design
    url(r'^upload/$', idoc_upload, name="idoc_upload"),
    url(r'^request/$', idoc_request, name="idoc_request"),
)

from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from idoc.models import IDocument
sqs = SearchQuerySet().models(IDocument)
# urls for search
urlpatterns += patterns('haystack.views',
	url(r'^search/$', SearchView(
		template="idoc/idoc_search.html",
		searchqueryset=sqs,
		form_class=ModelSearchForm
	), name="idoc_search"),
)
