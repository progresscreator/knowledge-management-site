from django.contrib import admin
from idea.models import CoolIdeaRequest, CoolIdea
from idea.models import CoolIdeaThumb
from idea.models import CoolIdeaRating
from idea.models import CoolIdeaFreezeCredit
from idea.models import CoolIdeaTransaction
from idea.models import CoolIdeaComment
from idea.models import CoolIdeaCommentThumb

admin.site.register(CoolIdeaRequest)
admin.site.register(CoolIdea)
admin.site.register(CoolIdeaThumb)
admin.site.register(CoolIdeaRating)
admin.site.register(CoolIdeaFreezeCredit)
admin.site.register(CoolIdeaTransaction)
admin.site.register(CoolIdeaComment)
admin.site.register(CoolIdeaCommentThumb)

