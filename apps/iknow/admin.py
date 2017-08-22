from iknow.models import Question, Answer, Rating, Thumb, QuestionTag
from iknow.models import QuestionComment, AnswerComment, QuestionAmendment
from iknow.models import QuestionFavorite
from iknow.models import AnswerTip
from django.contrib import admin

admin.site.register(Question)
admin.site.register(AnswerTip)
admin.site.register(Answer)
admin.site.register(Rating)
admin.site.register(Thumb)
admin.site.register(QuestionTag)
admin.site.register(QuestionComment)
admin.site.register(AnswerComment)
admin.site.register(QuestionFavorite)
admin.site.register(QuestionAmendment)
