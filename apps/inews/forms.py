from inews.models import AnnouncePost
from django.forms import ModelForm
from django import forms

class AnnouncePostForm(ModelForm):
    class Meta:
        model = AnnouncePost
        fields = ('title', 'budget', 'points_per_view', 'user_count', 'details', 'url', 'tags')

    title                = forms.CharField(max_length=256, required=True)
    budget      	 = forms.IntegerField(required=True, min_value=0, max_value=999999999, help_text="How much do you want to budget for publicity on this post?")
    points_per_view	 = forms.IntegerField(required=True, min_value=0, max_value=999999999, help_text="How much money will each user that reads your article receive?")
    details              = forms.CharField(max_length=2000, required=False, widget=forms.widgets.Textarea())
    user_count		 = forms.IntegerField(required=False, min_value=0, max_value=999999999, help_text="How many users do you want to reach with this post?")
    url			 = forms.URLField(max_length=256, required=False)
    tags		 = forms.CharField(required=False, max_length=512,
					help_text="Index your article with sufficient and accurate tags")

    def clean_title(self):
        if AnnouncePost.objects.filter(title__iexact=self.cleaned_data['title']):
            raise forms.ValidationError("Another post with that title already exists")

        return self.cleaned_data['title']

