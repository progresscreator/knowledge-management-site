#ibrarires
import simplejson
from django.http import HttpResponse
from iknow.models import Question
from idoc.models import IDocument
from haystack.query import SearchQuerySet
from django.core import serializers

#********************
#Results: input = query string,
#
#results_json: input = query string, output = http_response
#
    

def search_questions(query):
	sqs = SearchQuerySet().models(Question)
	results = sqs.auto_query(query)
	return results

def results_json(query):
    result_objs = search_questions(query)
    data = serializers.serialize("json", result_objs)
    return HttpResponse(data)

def search_documents(query):
	sqs = SearchQuerySet().models(IDocument)
	results = sqs.auto_query(query)
	return results


    

