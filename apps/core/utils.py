from googlevoice import Voice
from googlevoice.util import input
import BeautifulSoup
from django.contrib.auth.models import User

def sms_notify(number, text):
	voice = Voice()
	voice.login()
	voice.send_sms(number, text)

def sms_notify_list(number_list, text):
	voice = Voice()
	voice.login()
	for number in number_list:
		voice.send_sms(number, text)

def extractsms(htmlsms) :
	msgitems = []										# accum message items here
	#	Extract all conversations by searching for a DIV with an ID at top level.
	tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
	conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
	for conversation in conversations :
	#	For each conversation, extract each row, which is one SMS message.
		rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
		for row in rows :								# for all rows
		#	For each row, which is one message, extract all the fields.
			msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
			spans = row.findAll("span",attrs={"class" : True}, recursive=False)
			for span in spans :							# for all spans in row
				cl = span["class"].replace('gc-message-sms-', '')
				msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
			msgitems.append(msgitem)					# add msg dictionary to list
	return msgitems

def parse_phone_number(raw):
	number = ""
	for c in raw:
		if c.isdigit():
			number = number + c
	if len(number) == 10:
		return number
	else:
		return None

def parse_question_id(raw):
	id = ""
	index = 0
	for c in raw.strip():
		if c.isdigit():
			id = id + c
			index = index + 1
		else:
			break
	id = id.lstrip("0 ")
	body = raw[index:]
	return id, body.strip()

def map_number_to_user(number):
	assert number.isdigit() and len(number) == 10
	from core.models import Settings
	try:
		settings = Settings.objects.get(mobile=number)
		return settings.user
	except Exception, e:
		return None
#	if number == "5083188816":
#		return User.objects.get(username="daweishen")
#	elif number == "6179092101":
#		return User.objects.get(username="kwan")
#	elif number == "6179011065":
#		return User.objects.get(username="ALippman")

def verified_emails(users):
	emails = []
	for user in users:
		for emailaddress in user.emailaddress_set.all():
			if emailaddress.verified and emailaddress.primary:
				emails.append(emailaddress.email)
	return emails

def verified_phones(users):
	phones = []
	for user in users:
		from core.models import Settings
		if user.settings.new_q_notification_txt and \
			parse_phone_number(user.settings.mobile):
			phones.append(parse_phone_number(user.settings.mobile))
	return phones

def show_name(user):
	if user.get_full_name():
		return user.get_full_name()
	else:
		return user.username
