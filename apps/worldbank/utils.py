from worldbank.models import Transaction
from datetime import datetime
def worldbank_subsidize(receiver, ttype, question=None, points=None):
	amount_dict = {
		"AL": 2,  # Allocate points of a question on time
		"TU": 2,  # Thumb up or down on an answer
		"AC": 2,  # Leave a comment on an answer
		"DI": 3,  # Contribute a new design idea
		"KQC": 2, # Leavea a comment on a question
		"KFQ": 25, # Ask the first question
	}
	daily_limit_dict = {
		"AL": -1, # Allocate points of a question on time
		"TU": 5, # Thumb up or down on an answer
		"AC": 5, # Leave a comment on an answer
		"DI": 5, # Contribute a new design idea
		"KQC": 5, # Leavea a comment on a question
		"KFQ": -1, # Ask the first question
	}
	if not points:
		points = amount_dict[ttype]
	daily_limit = daily_limit_dict[ttype]
	if daily_limit > 0:
		today = datetime.now()
		this_morning = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
		same_trans_count = Transaction.objects.filter(time_stamp__gte=this_morning, flow_type="B", dst=receiver,
			app="S", ttype=ttype).count()
		if same_trans_count >= daily_limit:
			return 1 # error code 1: exceeds daily limit, no more rewards
	transaction = Transaction(time_stamp=datetime.now(), flow_type="B", dst=receiver,
		app="S", ttype=ttype, amount=points, question=question)
	transaction.save()
	transaction.execute()
	return 0
