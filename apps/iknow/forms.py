from django.forms import ModelForm
from iknow.models import Answer
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat

class QuestionForm(forms.Form):
	HOUR_CHOICES = (
		("0", _("Midnight")),
		("6",  _("6 AM")),
		("9",  _("9 AM")),
		("12", _("12 PM")),
		("15", _("3 PM")),
		("18", _("6 PM")),
		("21", _("9 PM")),
	)
	
	title		= forms.CharField(max_length=128, 
					label=_("Title"),
					error_messages={"required":_("The question title is required")},
					help_text=_("Provide a title of your question"))
	details		= forms.CharField(widget=forms.Textarea, required=False,
					label=_("Details"),
					help_text=_("More details of your question"))
	points_offered = forms.IntegerField(min_value=0, initial=0,
					label=_("Points offered"),
					error_messages={"required":_("Please provide the starting price")},
					help_text=_("How many points you are willing to offer"))
	end_date	= forms.DateField(label=_("End date"),
					help_text=_("When will your question expire?"))
	end_hour	= forms.ChoiceField(choices=HOUR_CHOICES, 
					label=_("End hour"),
					help_text=_("What time will your question expire exactly?"))
	tags        = forms.CharField(required=False, max_length=512,
					label=_("Tags"),
					help_text=_("Index your question with sufficient and accurate tags"))
	anonymous	= forms.BooleanField(initial=False,required=False,
					label=_("Anonymous"),
					help_text=_("Ask the question anonymously?"))
	hide_answers	= forms.BooleanField(initial=False, required=False,
					label=_("Hide answers"),
					help_text=_("Disallow users to review answers until expiration"))

class AnswerForm(ModelForm):
	answer_text	= forms.CharField(widget=forms.Textarea,label=_("Answer"),
					error_messages={"required":_("The answer field can't be empty")})
	anonymous	= forms.BooleanField(initial=False, required=False,
					label=_("Anonymous"),
					help_text=_("Answer anonymously?"))
	hidden		= forms.BooleanField(initial=False, required=False,
					label=_("Hidden"),
					help_text=_("Hide your answer to other users before the question expires?"))
	class Meta:
		model = Answer
		fields = ("answer_text", "anonymous", "hidden", "picture", "file")
