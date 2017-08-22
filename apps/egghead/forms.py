from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat

class EggheadForm(forms.Form):
	first_name = forms.CharField(max_length=30, label=_("First name"))
	last_name = forms.CharField(max_length=30, label=_("Last name"))
	email = forms.EmailField(label=_("Email"))

	gtalk = forms.EmailField(required=False, label=_("Google chat"))
	facebook = forms.CharField(max_length=32, label=_("Facebook ID"), required=False)
	twitter = forms.CharField(max_length=32, label=_("Twitter"), required=False)

	title = forms.CharField(max_length=64, label=_("Title"), required=False)
	affiliation = forms.CharField(max_length=128, label=_("Affiliation"), required=False)
	program_year = forms.CharField(max_length=32, label=_("Program/Year"), required=False)

	location = forms.CharField(max_length=40, label=_("Location"), required=False)
	website = forms.URLField(label=_("Website"), required=False)

	expertise_tags = forms.CharField(label=_("Expertise tags"), required=False, widget=forms.Textarea)
	prior_experiences = forms.CharField(label=_("Prior experiences"), required=False, widget=forms.Textarea)
	geographic_interests = forms.CharField(label=_("Geographic interest"), max_length=256, required=False)
	sector_interests = forms.CharField(label=_("Sector interests"), max_length=512, required=False)

	about = forms.CharField(label=_("About yourself"), required=False, widget=forms.Textarea)
	
