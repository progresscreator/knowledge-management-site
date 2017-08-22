from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext, string_concat
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, loader
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.contrib.sites.models import Site
from inews.forms import AnnouncePostForm
from inews.models import AnnouncePost, AnnouncePostThumb, AnnouncePostTransaction, UserRecord
from inews.models import NewsTag
from django.conf import settings
from datetime import datetime
from inews import utils
import logging
import core.utils

from egghead.models import get_egghead_from_user



@login_required
def inews_home(request, qtype="all", template="inews/announcepost_home.html"):
    
	for x in AnnouncePost.objects.iterator():
	    x.update_time()

	sortby = "normal"
	my_posts = None
   	articles = AnnouncePost.objects.filter(creator=request.user).filter(status="A")
	top_tags = NewsTag.objects.order_by("-count")[:10]

	if qtype=="budget":
		sortby = "budget"
	elif qtype=="ppv":
		sortby = "ppv"
	elif qtype=="votes":
		sortby = "votes"
	elif qtype=="time":
		sortby = "time"
	else:
		sortby = "normal"

	if sortby == "normal":
		my_posts = articles.order_by("-time_stamp", "-budget", "-thumbs")
	if sortby == "budget":
		my_posts = articles.order_by("-budget", "-time_stamp")
	if sortby == "ppv":
		my_posts = articles.order_by("-points_per_view", "-time_stamp")
	if sortby == "votes":
		my_posts = articles.order_by("-thumbs", "-time_stamp")
	if sortby == "time":
		my_posts = articles.order_by("-time_stamp", "-budget", "-thumbs")

	return render_to_response(template, 
				{
				 "my_posts": my_posts,
				 "top_tags" : top_tags,
				 },
				context_instance=RequestContext(request))

@login_required
def create_announcepost(request):
    """Create an AnnouncePost, defaulting the author to the logged-in user."""
    egghead = get_egghead_from_user(request.user)
    form_error = list()
    if request.method == 'POST':
        form = AnnouncePostForm(request.POST)
        form.user = request.user
	is_valid = True
	points_blank = False
	ppv_blank = False

	if request.POST['budget'].isdigit():
		if int(request.POST['budget']) > egghead.available_credits():
			is_valid = False
			form_error.append("Budget exceeds available credits")
	else:
		points_blank = True


	if request.POST['points_per_view'].isdigit():
		if int(request.POST['points_per_view']) > int(request.POST['budget']):
			is_valid = False
			form_error.append("Points Per View may not exceed total budget.")
	else:
		ppv_blank = True

        if form.is_valid() and is_valid:
            post = form.save(commit=False)
            post.creator = request.user
            post.time_stamp = datetime.now()
            post.date_check = datetime.now()
	    post.url = request.POST['url']

	    if points_blank:
		post.budget = 0

	    if ppv_blank:
		post.points_per_view = 0
		
	    # Tag Handling
            tags = form.cleaned_data["tags"]
	    cleaned_tags = []
	    for tag in tags.split(","):
		cleaned_tag = utils.clean_tag(tag)
		if cleaned_tag:
			cleaned_tags.append(cleaned_tag)
			tag_obj, created = NewsTag.objects.get_or_create(name=cleaned_tag)
					
			if not created: 
				tag_obj.update_count()
	    if cleaned_tags:
		post.tags = ", ".join(cleaned_tags)

            post.save()

            transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					src = request.user,
					app = "N",
					ttype = "NVN",
					amount = post.budget,
					announcepost = post)
	    transaction.save()
	    transaction.execute()

            return HttpResponseRedirect(post.get_absolute_url())
	
	else:
        	form_error.append("The form itself is not valid")

    else:
        form = AnnouncePostForm(initial={'author': request.user})
    		
    return render_to_response('inews/announcepost_form.html', {'form': form,
							       'form_error': form_error,
							       }, context_instance=RequestContext(request))

@login_required
def inews_announcepost(request, announcepost_id="-1", template="inews/announcepost_detail.html"):
	try: announcepost = AnnouncePost.objects.get(pk=announcepost_id)
	except AnnouncePost.DoesNotExist: announcepost = None
	thumbs = announcepost.announcepostthumb_set.order_by("-time_stamp")[:7]
	my_votes = announcepost.announcepostthumb_set.filter(thumber=request.user)\
				.order_by("-time_stamp")
	my_vote_count = my_votes.count()
	
	announcepost.update_time()

	# Functionality: First time a user views a story, they should get (user-determined PPV) funds from the World Bank.
	is_new = False
	is_legal = True
	reward = False
	
	# Check for same user as poster
	if announcepost.creator == request.user:
		is_legal = False
		
	# Check that post is actually active
	if announcepost.status != "A":
		is_legal = False

	if is_legal:
	
		# Determine whether user is new or not
		is_new = announcepost.is_first_time_reader(request.user)


		# If new, set reward flag
		if is_new: 
			reward = True

			# Add user to the viewed_users list
			user_record = UserRecord(announcepost=announcepost,
							viewer=request.user, time_stamp=datetime.now())
			user_record.save()

		# If reward flag is set, alert the user.
		if reward:
			# Get PPV Amount
			amt = announcepost.points_per_view

			# Alert User
			msgtext = "You have recevied {0:d} points for viewing this article.".format(amt)
			request.user.message_set.create(message=msgtext)

			if announcepost.points_per_view > announcepost.budget:
				announcepost.points_per_view = 0
				amt = announcepost.budget
				announcepost.budget = 0
				

			# Transfer PPV funds to their accout from the World Bank.
			transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					dst = request.user,
					app = "N",
					ttype = "XXX",
					amount = amt,
					announcepost = announcepost)
	    	 	transaction.save()
	    	 	transaction.execute()

			# Deduct PPV funds from the budget
		 	announcepost.budget = announcepost.budget - announcepost.points_per_view
		 	announcepost.save()

	if announcepost.url and not announcepost.details:
		template="inews/announcepost_urldetail.html"

	if announcepost.url and announcepost.details:
		template="inews/announcepost_detail.html"
		
	return render_to_response(template, {
					"announcepost": announcepost,
					"thumbs" : thumbs,
					"my_votes" : my_votes,
                    "my_vote_count" : my_vote_count,
				},
				context_instance=RequestContext(request))

@login_required
def inews_tag(request, tag_id, template="inews/inews_tag.html"):
	try:
		tag = NewsTag.objects.get(pk=tag_id)
	except Exception, e:
		tag = NewsTag.objects.all()[0]
	return render_to_response(template, 
				{"tag": tag,
				},
				context_instance=RequestContext(request))

@login_required
def inews_thumb_check(request):
	if request.method == "POST":
		try:
			announcepost_id = request.POST["id"]
			announcepost = AnnouncePost.objects.get(pk=announcepost_id)
			if announcepost.creator == request.user: 
				return HttpResponse("2")
			else: 
				return HttpResponse("1")
		except Exception, e:
			dlogger.warning(e)
			return HttpResponse("1")


@login_required
def inews_thumbup(request, announcepost_id):
	"""Runs after user thumbs a post up. Deducts the appropriate amount of
	money from the user based on cost function."""
	try:
		announcepost = AnnouncePost.objects.get(pk=announcepost_id)
	except AnnouncePost.DoesNotExist:
		announcepost = None

	# Get price of vote
	price = announcepost.get_thumb_price(request.user)

	# Get N: # of times user has voted on this post
	first_vote = False
	thumb_n = announcepost.get_n_thumb_count(request.user)
	if thumb_n == 1:
		first_vote = True

	# Check that user is not creator
	is_valid = True
	if announcepost.creator == request.user:
		is_valid = False

	# Perform a balance check
	balance_check = request.user.egghead.wealth_notes - price
	if balance_check < 0:
		request.user.message_set.create(message="Not enough funds to vote.")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	
	# Return if invalid due to prior checks (creator is user)	
	elif is_valid == False:
		request.user.message_set.create(message="You cannot vote for yourself.")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

	else:
	
		# Trigger if First Vote
		if first_vote:
			request.user.message_set.create(message="You have received 2 points for casting your first vote on the article " + announcepost.title)
		
		# Create AnnouncePost Vote Object
		AnnouncePostThumb.objects.create(announcepost=announcepost, thumber=request.user, up_or_down="U", time_stamp=datetime.now())

		# Update vote count by counting Vote Objects
		announcepost.update_thumbs()

		# Set announcepost aggregate value to reflect addition of credited ppv points
		announcepost.budget += announcepost.points_per_view

		# Save the announcepost.
		announcepost.save()

		# Send a message to the voter
		request.user.message_set.create(message="Voted up post.")

		# First Vote Payment
		if first_vote:
			amt = 2
			# Transfer 2 points from the World Bank.
			transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					dst = request.user,
					app = "N",
					ttype = "XXX",
					amount = amt,
					announcepost = announcepost)
	    	 	transaction.save()
	    	 	transaction.execute()

		# Mark the voting source
		source = request.user

		# Perform the transfer
            	transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					src = request.user,
					app = "N",
					ttype = "NVN",
					amount = price,
					announcepost = announcepost)
	   	transaction.save()
	    	transaction.execute()

		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@login_required
def inews_thumbdown(request, announcepost_id):
	"""Runs after user thumbs a post down. Deducts the appropriate amount of
	money from the user based on cost function."""
	try:
		announcepost = AnnouncePost.objects.get(pk=announcepost_id)
	except AnnouncePost.DoesNotExist:
		announcepost = None

	# Get price of vote
	price = announcepost.get_thumb_price(request.user)

	# Get N: # of times user has voted on this post
	first_vote = False
	thumb_n = announcepost.get_n_thumb_count(request.user)
	if thumb_n == 1:
		first_vote = True

	# Check that user is not creator
	is_valid = True
	if announcepost.creator == request.user:
		is_valid = False

	# Perform a balance check
	balance_check = request.user.egghead.wealth_notes - price
	if balance_check < 0:
		request.user.message_set.create(message="Not enough funds to vote.")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	
	elif is_valid == False:
		request.user.message_set.create(message="You cannot vote for yourself.")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

	else:

		# Trigger if First Vote
		if first_vote:
			request.user.message_set.create(message="You have received 2 points for casting your first vote on the article " + announcepost.title)

		# Create AnnouncePost Vote Object
		AnnouncePostThumb.objects.create(announcepost=announcepost, thumber=request.user, up_or_down="D", time_stamp=datetime.now())

		# Update vote count by counting Vote Objects
		announcepost.update_thumbs()

		# Set announcepost aggregate value to reflect addition of new price
		announcepost.budget -= announcepost.points_per_view

		# Save the announcepost.
		announcepost.save()

		# Send a message to the voter
		request.user.message_set.create(message="Voted down post.")

		# First Vote Payment
		if first_vote:
			amt = 2
			# Transfer 2 points from the World Bank.
			transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					dst = request.user,
					app = "N",
					ttype = "XXX",
					amount = amt,
					announcepost = announcepost)
	    	 	transaction.save()
	    	 	transaction.execute()

		# Mark the voting source
		source = request.user

		# Perform the transfer
            	transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					src = request.user,
					app = "N",
					ttype = "NVN",
					amount = price,
					announcepost = announcepost)
	   	transaction.save()
	    	transaction.execute()

		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


@login_required
def inews_articles(request, template="inews/inews_articles.html"):
	objs = AnnouncePost.objects.all()
	return render_to_response(template, 
				{"objs": objs,},
				context_instance=RequestContext(request))

@login_required
def inews_tipping(request):

    if request.method == "POST":
        try:
            tip_type = request.POST["type"]
            tip_id   = request.POST["id"]
            tip_amt  = int(request.POST["tip"])

            msgtext = "tip_id: {0:d}".format(tip_id)
            request.user.message_set.create(message=msgtext)

            msgtext = "tip_amt: {0:d}".format(tip_amt)
            request.user.message_set.create(message=msgtext)

            if tip_type == "author":
                recipient = Users.objects.get(pk=tip_id)

                # Transfer from user to post author
                # Mark the source
                source = request.user

		        # Perform the transfer
            	transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					src = source,
                    dst = recipient, 
					app = "N",
					ttype = "NVN",
					amount = tip_amt)
                transaction.save()
                transaction.execute()
                
            elif tip_type == "post":
                recipient = announcepost.objects.get(pk=tip_id)

                # Transfer from user to world bank
                # Mark the source
                source = request.user

                # Perform the transfer
                transaction = AnnouncePostTransaction(
					time_stamp = datetime.now(),
					flow_type = "I",
					src = request.user,
					app = "N",
					ttype = "XXX",
					amount = tip_amt)
                transaction.save()
                transaction.execute()

            return HttpResponse("0")
		        
        except Exception, e:
            print e
            klogger.info(e)

    return HttpResponse("1")


@login_required
def inews_help(request, template="inews/inews_help.html"):

	return render_to_response(template, 
				{},
				context_instance=RequestContext(request))

def inews_ajax_articles(request, 
				qtype="all",
				tag_id=None, 
				template="inews/inews_ajax_articles.html"):
	
	home = False
	if qtype.startswith("h_"):
		home = True
	if qtype == "all":
		articles = AnnouncePost.objects.all()
		title = _("All articles")
	elif qtype == "top_value" or qtype == "h_top_value":
		title = _("News articles of the highest value")
		articles = AnnouncePost.objects.filter(status="A")
	elif qtype == "top_votes" or qtype == "h_top_votes":
		title = _("News articles with highest votes")
		articles = AnnouncePost.objects.filter(status="A")
	elif qtype == "whats_new" or qtype == "h_whats_new":
		title = _("Upcoming news articles")
		articles = AnnouncePost.objects.filter(status="A")
	elif qtype == "inactive" or qtype == "h_inactive":
		title = _("Inactive news articles")
		articles = AnnouncePost.objects.filter(status="E")
	else:
		articles = None

	# Tag Handling
	if tag_id:
		tag = NewsTag.objects.get(pk=tag_id)
		title = _("iNews Articles tagged with %(tag_name)s") % {"tag_name": tag.name}
		articles = AnnouncePost.objects.filter(tags__icontains=tag.name)

	if not articles:
		return render_to_response(template, 
					{"objs": None,
					 "title": title,
					 "order": "time", 
					 "page": 0,
					 "total_pages": 0,
					 "qtype": qtype,
					 "home": home,
					 },
					context_instance=RequestContext(request))
	order = "time"
	if qtype == "top_value" or qtype == "h_top_value":
		order = "budget"
	elif qtype == "top_votes" or qtype == "h_top_votes":
		order = "votes"
	page = 1
	if request.method == "GET":
		if request.GET.has_key("order"):
			order = request.GET["order"]
		if request.GET.has_key("page"):
			page = int(request.GET["page"])
	if order == "time":
		q_ordered = articles.order_by("-time_stamp")
	elif order == "budget":
		q_ordered = articles.order_by("-budget")
	elif order == "votes":
		q_ordered = articles.order_by("-thumbs")
	paginator = Paginator(q_ordered, 40)

	return render_to_response(template, 
				{"objs":paginator.page(page),
				 "title": title,
				 "order": order, 
				 "page": page,
				 "total_pages": paginator.num_pages,
				 "qtype": qtype,
				 "home": home,
				 },
				context_instance=RequestContext(request))

