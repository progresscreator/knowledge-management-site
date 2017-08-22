def clean_tag(tag):
	stripped_tag = tag.strip()
	if not stripped_tag:
		return None
	return " ".join(word.lower().capitalize() for word in stripped_tag.split())


def migrate_tips():
	from worldbank.models import Transaction
	from iknow.models import AnswerTip, Answer
	for tr in Transaction.objects.filter(flow_type="I", app="K", ttype="TI"):
		answer = Answer.objects.get(question=tr.question, answerer=tr.dst)
		tipper = tr.src
		time_stamp = tr.time_stamp
		amount = tr.amount
		at = AnswerTip(answer=answer, tipper=tipper, time_stamp=time_stamp,amount=amount)
		at.save()
	
if __name__ == "__main__":
	print clean_tag("hello world")
	print clean_tag("   en?  ")
