from idoc.models import IDocument, IDocDownload, IDocRating, IDocTransaction
from idoc.models import IDocFreezeCredit
from django.contrib import admin

admin.site.register(IDocument)
admin.site.register(IDocDownload)
admin.site.register(IDocRating)
admin.site.register(IDocTransaction)
admin.site.register(IDocFreezeCredit)

