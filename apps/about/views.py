from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings

from egghead.models import get_egghead_from_user
from core.models import Feature

# Python libraries
import os
from datetime import datetime
from datetime import timedelta

@login_required
def what_next(request, template="about/what_next.html"):
	egghead = get_egghead_from_user(request.user)
	features = Feature.objects.order_by("-creation_date")[:10]	
	return render_to_response(template, 
				{"egghead": egghead,
				 "features": features,	
				},
				context_instance=RequestContext(request))
