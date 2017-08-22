from worldbank.models import FreezeCreditDesignIdea
from idesign.models import DesignIdeaFreezeCredit

def migrate_designidea_freezecredits():
	for o in FreezeCreditDesignIdea.objects.all():
		n = DesignIdeaFreezeCredit(
				designidea=o.designidea,
				is_donate=o.is_donate,
				time_stamp=o.time_stamp,
				fuser=o.fuser,
				ftype=o.ftype,
				app=o.app,
				ttype=o.ttype,
				amount=o.amount,
				cleared=o.cleared,
			)
		n.save()
