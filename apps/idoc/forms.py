from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from idoc.models import IDocument, IDocRequest
from django import forms

class IDocRequestForm(forms.ModelForm):
	HOUR_CHOICES = (
		("0", _("Midnight")),
		("6",  _("6 AM")),
		("9",  _("9 AM")),
		("12", _("12 PM")),
		("15", _("3 PM")),
		("18", _("6 PM")),
		("21", _("9 PM")),
	)
	title		= forms.CharField(max_length=256,
					error_messages={"required":_("The title of the requested document is required")},
					help_text=_("Provide a title of the document you request"))
	details		= forms.CharField(widget=forms.Textarea, required=False,
					help_text=_("Provide a bit more details about the document you request"))
	points_offered = forms.IntegerField(min_value=0, initial=0,
					error_messages={"required":_("Please provide the starting price")},
					help_text=_("How many points you are willing to offer"))
	end_date	= forms.DateField(help_text=_("When will your document request expire?"))
	end_hour	= forms.ChoiceField(choices=HOUR_CHOICES, 
					help_text=_("What time will your question expire exactly?"))
	anonymous	= forms.BooleanField(initial=False,required=False,
					help_text=_("Request the document anonymously?"))
	tags		= forms.CharField(required=False, max_length=512,
					help_text=_("Index your document with sufficient and accurate tags"))

	class Meta:
		model = IDocRequest
		fields = ("title",
				 "details",
				 "points_offered",
				 "anonymous",
				 "tags",
				)

class IDocumentForm(forms.ModelForm):
	title		= forms.CharField(max_length=256,
					error_messages={"required":_("The title of your document is required")},
					help_text=_("Provide a title of your document"))
	details		= forms.CharField(widget=forms.Textarea, required=False,
					help_text=_("Provide a bit more details about your document"))
	version		= forms.CharField(required=False, max_length=10, initial="1.0",
					help_text=_("Provide a version number of your document (optional)"))
	points_needed	= forms.IntegerField(initial=0,
					error_messages={"required":_("Specify the needed points")},
					help_text=_("Points charged when others download your document"))
	tags		= forms.CharField(required=False, max_length=512,
					help_text=_("Index your document with sufficient and accurate tags"))
	url			= forms.URLField(required=False, max_length=200,verify_exists=True,
					help_text=_("Provide a link pointing to your document"))
	file		= forms.FileField(required=False,
					help_text=_("Finally, please upload your document"))
	class Meta:
		model = IDocument
		fields = ("title",
				 "details",
				 "anonymous",
				 "version",
				 "points_needed",
				 "tags",
				 "url",
				 "file",
				)

