# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.files import File
from knowledge_web import settings

from iquest.forms import RequestForm, ResponseForm
from iquest.models import Request, Response
# import from floor apps

# Python libraries
import os
from datetime import datetime
from datetime import timedelta

def iquest_home(request, template="iquest/iquest_home.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))

def iquest_ask(request, template="iquest/iquest_ask.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))

def iquest_requests(request, template="iquest/iquest_requests.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))

def iquest_request(request, request_id, template="iquest/iquest_request.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))

def iquest_response(request, request_id, template="iquest/iquest_response.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))
