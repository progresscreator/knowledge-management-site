from idesign.models import DesignIdea
from django.forms import ModelForm
from django import forms

class DesignIdeaForm(ModelForm):
	title				= forms.CharField(max_length=256, required=True)
	points_offered		= forms.IntegerField(initial=0,
		help_text="Optional, but a way to show your appreciation and incentive for developers")

	class Meta:
		model = DesignIdea
		fields = ('title', 'details', 'points_offered', 'tags')
