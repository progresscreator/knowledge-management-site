from worldbank.models import Transaction
from idoc.models import IDocTransaction, IDocument

def migrate_du_transactions():
	dts = Transaction.objects.exclude(document__isnull=True)
	for t in dts:
		try:
			idocument = IDocument.objects.get(olddoc=t.document)
			idt = IDocTransaction(
					time_stamp=t.time_stamp,
					flow_type=t.flow_type,
					src=t.src,
					dst=t.dst,
					app=t.app,
					ttype="DUD",
					amount=t.amount,
					idocument=idocument
				)
			idt.save()
			print "transaction migrated for %s" % idocument.title
		except Exception, e:
			print "Error: %s" % e
