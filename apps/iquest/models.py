from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RequestCategory(models.Model):
	name				= models.CharField(max_length=32)
	parent				= models.ForeignKey("self")

	def __unicode__(self):
		return self.name

class Request(models.Model):
	REQUEST_STATUS = (
		("A", "Active"),
		("W", "Withdrawn"),
		("P", "Expired and Pending"),
		("S", "Solved and Closed"),
		("U", "Unsolved and Closed"),
		("E", "Extended"),
		("I", "Illegal"),
	)
	SHARING_OPTIONS = (
		("P", "Public"),
		("F", "Friends"),
		("G", "Groups"),
		("B", "Both friends and selected groups"),
		("U", "Targeted Users"),
	)
	requester			= models.ForeignKey(User, related_name="requests_made")
	time_stamp			= models.DateTimeField()

	request_title		= models.CharField(max_length=128)
	request_text		= models.TextField(blank=True)
	tags				= models.CharField(max_length=512, blank=True)
	categories			= models.ManyToManyField(RequestCategory, blank=True, null=True)

	status				= models.CharField(max_length=1, choices=REQUEST_STATUS, default="A")
	sharing				= models.CharField(max_length=1, choices=SHARING_OPTIONS, default="P")
	anonymous			= models.BooleanField(default=False)

	points_offered		= models.IntegerField(default=0)
	points_final		= models.IntegerField(default=0)
	points_expiration	= models.DateTimeField(blank=True, null=True)

	thumb_up			= models.IntegerField(default=0)
	thumb_down			= models.IntegerField(default=0)

	to_users			= models.ManyToManyField(User, related_name="requests_received",
							blank=True, null=True)
	to_groups			= models.ManyToManyField("tribes.Tribe", blank=True, null=True)

	visits				= models.IntegerField(default=0)

	def __unicode__(self):
		return self.request_title

	def get_responses(self, standard=None):
		if not standard:
			return self.response_set.order_by("-time_stamp")
		return self.response_set.order_by("-time_stamp")
	
	def response_count(self):
		return self.response_set.count()

	def time_string_s(self):
		return self.time_stamp.strftime("%m-%d %I:%M%p")

	def time_string_l(self):
		return self.time_stamp.strftime("%Y-%m-%d,%I:%M%p")
	
	def display_name(self):
		if self.anonymous:
			return "A Egghead"
		return self.requester.get_full_name()


class Response(models.Model):
	RESPONSE_STATUS = (
		("R", "Regular"),
		("E", "Edited"),
		("I", "Illegal"),
		("W", "Withdrawn"),
	)
	SHARING_OPTIONS = (
		("P", "Public"),
		("F", "Friends"),
		("G", "Groups"),
		("B", "Both friends and selected groups"),
		("U", "Targeted Users"),
		("A", "Asker"),
	)
	responser			= models.ForeignKey(User, related_name="responses_made")	
	request			= models.ForeignKey(Request)

	time_stamp			= models.DateTimeField()
	response_text		= models.TextField()
	tags				= models.CharField(max_length=512, blank=True)
	
	status				= models.CharField(max_length=1, choices=RESPONSE_STATUS, default="R")
	sharing				= models.CharField(max_length=1, choices=SHARING_OPTIONS, default="P")

	thumb_up			= models.IntegerField(default=0)
	thumb_down			= models.IntegerField(default=0)
	rating_by_requester	= models.IntegerField(default=5)
	anonymous			= models.BooleanField(default=False)

	points_received		= models.IntegerField(default=0)
	
	to_users			= models.ManyToManyField(User, related_name="responses_shared",
							blank=True, null=True)
	to_groups			= models.ManyToManyField("tribes.Tribe", blank=True, null=True)

	picture				= models.ImageField(upload_to="iquest/responses/pictures/", blank=True, null=True)
	file				= models.FileField(upload_to="iquest/responses/files/", blank=True, null=True)

	visits				= models.IntegerField(default=0)

	def __unicode__(self):
		return self.response_text
	
class Rating(models.Model):
	TYPE_CHOICES = (
		("E", "As a elicitor"),
		("C", "As a contributor"),
	)
	rater				= models.ForeignKey(User, related_name="iquest_rating_given")
	receiver			= models.ForeignKey(User, related_name="iquest_rating_received")
	rating              = models.DecimalField(max_digits=4, decimal_places=2)
	request				= models.ForeignKey(Request)
	rtype				= models.CharField(max_length=1, choices=TYPE_CHOICES)
	time_stamp			= models.DateTimeField()

	def __unicode__(self):
		return rater.get_full_name() + " gives " + receiver.get_full_name() + " " + str(rating)
	
