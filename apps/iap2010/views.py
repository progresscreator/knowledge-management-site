# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.sites.models import Site

# Python libraries
import os
import logging
from datetime import datetime
from datetime import timedelta

klogger = logging.getLogger("pwe.iknow")

def iap2010_home(request, template="iap2010/iap2010_home.html"):
	return render_to_response(template, 
				context_instance=RequestContext(request))
