from googlevoice import Voice
from googlevoice.util import input
from django.core.management.base import NoArgsCommand
from core.utils import extractsms, parse_phone_number, parse_question_id
from core.utils import map_number_to_user
from iknow.models import Question,Answer
from datetime import datetime

class Command(NoArgsCommand):
    help = 'Attempt to check voice messages for answers'
    
    def handle_noargs(self, **options):
		voice = Voice()
		voice.login()
		smses = voice.sms()
		to_be_deleted = []
		for msg in extractsms(voice.sms.html):
			if msg["from"] != "Me":
				print msg
				sender_number = parse_phone_number(msg["from"])				
				if sender_number:
					answerer = map_number_to_user(sender_number)
					if not answerer: continue
				id, body = parse_question_id(msg["text"])
				print "id: %s" % str(id)
				if not id: continue
				print "body: %s" % str(body)
				try:
					question = Question.objects.get(pk=id)
					# A few checks here
					if not body:
						print "answer is empty"
						continue
					if not question.answerable(): 
						print "answer is answerable"
						continue
					if question.asker == answerer: 
						print "Asker is the same as the answerer"
						continue
					if question.is_answered_by(answerer):
						answer = Answer.objects.get(question=question, answerer=answerer)
						answer.answer_text = answer.answer_text + "\n" + body
						answer.edit_time_stamp = datetime.now()
					else:
						answer = Answer(answerer=answerer, question=question, time_stamp=datetime.now(),
							answer_text=body)
					answer.save()
					to_be_deleted.append(msg["id"])
				except Exception, e:
					print e
		for message in voice.sms().messages:
			print "start to deleting messages ..."	
			print message.id
			if message.id in to_be_deleted:
				message.delete()
		
