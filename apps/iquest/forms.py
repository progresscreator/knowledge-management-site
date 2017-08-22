from django.forms import ModelForm
from iquest.models import Request, Response

class RequestForm(ModelForm):
	class Meta:
		model = Request
		fields = ("question_title", "question_text", "tags", "points_offered")

class ResponseForm(ModelForm):
	class Meta:
		model = Response
		fields = ("answer_text", "picture", "file", "anonymous")
