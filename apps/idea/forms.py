from idea.models import CoolIdea
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

class CoolIdeaForm(forms.ModelForm):
	HOUR_CHOICES = (
		("0", _("Midnight")),
		("6",  "6 AM"),
		("9",  "9 AM"),
		("12", "12 PM"),
		("15", "3 PM"),
		("18", "6 PM"),
		("21", "9 PM"),
	)
	title		= forms.CharField(max_length=256,
					label=_("Title"),
					error_messages={"required":_("The title of your cool idea is required")},
					help_text=_("Provide a title of your cool idea"))
	internal_col	= forms.CharField(widget=forms.Textarea, required=False,
					label=_("Collaborators"),
					help_text=_("Who are collaborators of your idea inside Barter? Type their names or \
						usernames and select from the dropdown menu. Don't change how it's formatted."))
	external_col	= forms.CharField(max_length=512, required=False,
						label=_("External collaborators"),	
						help_text=_("Who are collaborators of your idea external to Barter?\
						List their names separated by commas."))
	details		= forms.CharField(widget=forms.Textarea, required=False,
					label=_("Details"),
					help_text=_("More details about your cool idea"))
#	version		= forms.CharField(required=False, max_length=10, initial="1.0",
#					label=_("Version"),
#					help_text=_("Provide a version number that helps track your idea (optional)"))
#	points_offered	= forms.IntegerField(initial=0,
#					label=_("Points offered"),
#					error_messages={"required":_("Specify the points you offer")},
#					help_text=_("Points offered when others contribute to your idea"))
#	end_date	= forms.DateField(required=False,
#					label=_("End date"),
#					help_text=_("The due date when you need to allocate offered points \
#						among contributors to your idea."))
#	end_hour	= forms.ChoiceField(required=False, choices=HOUR_CHOICES, 
#					label=_("End hour"),
#					help_text="What time exactly?")
	tags		= forms.CharField(required=False, max_length=512,
					label=_("Tags"),
					help_text=_("Index your idea with sufficient and accurate tags. Use a\
						comma-separated list of tags. Choose from the dropdown menu or type\
						a new tag."))
	file1		= forms.FileField(required=False,
					label=_("File"),
					help_text=_("You can upload a document together with your idea"))
	picture1	= forms.ImageField(required=False,
					label=_("Picture"),
					help_text=_("You can upload an image associated with your idea (Optional)\
						which can be directly rendered and displayed on the idea interface."))
#	picture2	= forms.ImageField(required=False,
#					label=_("Picture 2"),
#					help_text=_("second image (optional)"))
#	file2		= forms.FileField(required=False,
#					label=_("File 2"),
#					help_text=_("second document (optional)"))
#	file3		= forms.FileField(required=False,
#					label=_("File 3"),
#					help_text=_("third document (optional)"))
	class Meta:
		model = CoolIdea
		fields = ("title",
				 "internal_col",
				 "external_col",
				 "details",
#				 "version",
#				 "points_offered",
#				 "end_date",
#				 "end_hour",
				 "tags",
				 "file1",
				 "picture1",
#				 "picture2",
#				 "file2",
#				 "file3",
				)
