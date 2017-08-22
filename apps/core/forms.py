from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from core.models import Settings, Feature

class SettingsForm(forms.ModelForm):
	new_q_notification_txt = forms.BooleanField(
		required=False,
		label=_("iKnow SMS"),
		help_text=_("Receive an SMS on your mobile phone when a new question enters the market"))
	mobile = forms.CharField(
		required=False,
		label=_("Mobile No."),
		help_text=_("Mobile phone number in the format of 0123456789"))
	new_q_notification_email = forms.BooleanField(
		required=False,
		label=_("iKnow Email"),
		help_text=_("Receive an email when a new question enters the market"))
	new_feature_email = forms.BooleanField(
		required=False,
		label=_("New feature updates"),
		help_text=_("Receive updates on new features through emails"))
	class Meta:
		model = Settings
		exclude = ('user',)

class FeatureForm(forms.ModelForm):
	class Meta:
		model = Feature
		exclude = ('committer', 'creation_date',)
