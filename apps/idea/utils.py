from idea.models import CoolIdeaTransaction
from datetime import datetime
def worldbank_subsidize(receiver, ttype, coolidea=None, idearequest=None, 
						coolideacomment=None, points=None):
	amount_dict = {
		"ITU": 2,  # Thumb up/down on an idea
		"ITC": 2,  # Thumb up/down on a comment to an idea
		"IRT": 2,  # Rate an idea
		"IIC": 2,  # Leave a comment on an idea
	}
	daily_limit_dict = {
		"ITU": 5, # Thumb up or down on an answer
		"ITC": 5,  # Thumb up/down on a comment to an idea
		"IRT": 5, # Rate an idea
		"IIC": 5,  # Leave a comment on an idea
	}
	if not points:
		points = amount_dict[ttype]
	daily_limit = daily_limit_dict[ttype]
	if daily_limit > 0:
		today = datetime.now()
		this_morning = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
		same_trans_count = CoolIdeaTransaction.objects.filter(time_stamp__gte=this_morning, 
			flow_type="B", dst=receiver, app="S", ttype=ttype).count()
		if same_trans_count >= daily_limit:
			return 1 # error code 1: exceeds daily limit, no more rewards
	transaction = CoolIdeaTransaction(time_stamp=datetime.now(), flow_type="B", dst=receiver,
		app="S", ttype=ttype, amount=points, coolidea=coolidea, idearequest=idearequest,
		coolideacomment=coolideacomment)
	transaction.save()
	transaction.execute()
	return 0
