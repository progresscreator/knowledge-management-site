from worldbank.models import FreezeCreditAuction
from iauction.models import AuctionFreezeCredit

def migrate_auction_freezecredits():
	for o in FreezeCreditAuction.objects.all():
		n = AuctionFreezeCredit(
				bid=o.bid,
				time_stamp=o.time_stamp,
				fuser=o.fuser,
				ftype=o.ftype,
				app=o.app,
				ttype=o.ttype,
				amount=o.amount,
				cleared=o.cleared,
			)
		n.save()
