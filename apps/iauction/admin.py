from iauction.models import AuctionProduct, AuctionBid, AuctionDeal, AuctionFreezeCredit
from django.contrib import admin

admin.site.register(AuctionProduct)
admin.site.register(AuctionBid)
admin.site.register(AuctionDeal)
admin.site.register(AuctionFreezeCredit)

