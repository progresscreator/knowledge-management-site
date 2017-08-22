import os.path
import csv
from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress
from egghead.models import EggHead
import logging

elogger = logging.getLogger("pwe.egghead")

def invalidreg(emailkey):
	import re
	emailregex = "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3\
				})(\\]?)$"
	if len(emailkey) > 7:
		if re.match(emailregex, emailkey) != None:
			return False
		return True
	else:
		return True

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
	        yield line.encode('utf-8')

def french_import_1():
	current_dir = os.path.abspath(os.path.dirname(__file__))
	userfile = open(os.path.join(current_dir, "french_class_1.csv"), "rb")
	
	reader = csv.reader(userfile, delimiter=";")
	index = 0
	successes = 0
	for row in reader:
		if index == 0: 
			index += 1
			continue
		print row
		unique_id = row[0].strip()
		first_name = row[1].strip()
		last_name = row[2].strip()
		print "Row %d: ID: %s" % (index, unique_id)
		print "Firstname: %s lastname: %s" % (first_name, last_name)
		email = row[3].strip()
		if invalidreg(email):
			print "Invalid email address: %s" % email
			index += 1
			elogger.info("ID: %s Name: %s %s Invalid email address: %s" % (unique_id, 
				first_name, last_name, email))
			continue
		desired_username = (email.split("@")[0]).lower().replace(".", "_").replace("-", "_")
		print "Valid email: %s, username desired: %s\n" % (email, desired_username)

		user, created = User.objects.get_or_create(username=desired_username,
			email=email)
		user.set_password(unique_id)
		user.save()
		try:
			user.first_name = first_name
			user.save()
		except Exception, e:
			elogger.info("Error occured when saving first name: %s" % e)
			print e
			user.first_name = ""
			user.save()
		try:
			user.last_name = last_name
			user.save()
		except Exception, e:
			elogger.info("Error occured when saving last name: %s" % e)
			print e
			user.last_name = ""
			user.save()

		confirmed_email, created = EmailAddress.objects.get_or_create(user=user, email=email)
		if created:
			confirmed_email.verified = True
			confirmed_email.primary = True
			confirmed_email.save()
		
		egghead, created = EggHead.objects.get_or_create(user=user)
		if created:
			egghead.unique_id = unique_id
			egghead.save()
		index += 1
		successes += 1
		print "%d accounts have been successfully created " % successes


def dvimport():
	current_dir = os.path.abspath(os.path.dirname(__file__))
	userfile = open(os.path.join(current_dir, "user.csv"), "rb")
	
	reader = csv.reader(userfile, delimiter=",", quotechar='"')
	index = 1
	for row in reader:
		print row
		email = row[2].strip()
		desired_username = (email.split("@")[0]).lower()
		first_name = row[0].strip()
		last_name = row[1].strip()
		# print "Row %d: firstname: %s lastname: %s" % (index, first_name, last_name)
		# print "email: %s, username desired: %s" % (email, desired_username)

		user, created = User.objects.get_or_create(username=desired_username,
			first_name=first_name, last_name=last_name,
			email=email)
		if created:
			user.set_password(desired_username)
			user.save()

		confirmed_email, created = EmailAddress.objects.get_or_create(user=user, email=email)
		if created:
			confirmed_email.verified = True
			confirmed_email.primary = True
			confirmed_email.save()
		affiliation = row[3]
		program_year = row[4]
		prior_experiences = row[5]
		geographic_interests = row[6]
		sector_interests = row[7]
		
		egghead, created = EggHead.objects.get_or_create(user=user)
		if created:
			egghead.affiliation = affiliation
			egghead.program_year = program_year
			egghead.prior_experiences = prior_experiences
			egghead.geographic_interests = geographic_interests
			egghead.sector_interests = sector_interests
			egghead.save()

		index += 1
