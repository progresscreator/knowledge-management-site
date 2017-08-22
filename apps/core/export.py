import csv
from iknow.models import Question
from iauction.models import AuctionDeal

def export_question_stats():
	f = open("/home/daweishen/Desktop/question_stats.csv", "wb")
	writer = csv.writer(f)
	writer.writerow(["Title", "Date", "Offered", "Allocated", "Status", "Answers"])
	for question in Question.objects.all():
		if question.status in ("S", "F"):
			allocated = question.points_offered
		else:
			allocated = 0
		alist = [question.question_title, question.date_string(), question.points_offered,
			allocated, question.status, question.answer_count()]
		writer.writerow(alist)

def export_ibay_stats():
	f = open("/home/daweishen/Desktop/ibay_stats.csv", "wb")
	writer = csv.writer(f)
	writer.writerow(["Product", "Bids", "Winning price"])
	for deal in AuctionDeal.objects.all():
		alist = [deal.bid.product.name, deal.bid.product.total_bids(), deal.bid.amount] 
		writer.writerow(alist)
