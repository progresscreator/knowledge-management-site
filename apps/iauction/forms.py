from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy, string_concat
from iauction.models import AuctionProduct
from django import forms

class AuctionProductForm(forms.Form):
	HOUR_CHOICES = (
		("0", _("Midnight")),
		("6",  _("6 AM")),
		("9",  _("9 AM")),
		("12", _("12 PM")),
		("15", _("3 PM")),
		("18", _("6 PM")),
		("21", _("9 PM")),
	)
	
	name		= forms.CharField(max_length=128, 
					error_messages={"required":_("The product name is required")},
					help_text=_("Name of the product you want to sell on iBay"))
	details		= forms.CharField(widget=forms.Textarea, required=False,
					help_text=_("Attach a nice description to attract others"))
	start_price = forms.IntegerField(min_value=1,
					error_messages={"required":_("Please provide the starting price")},
					help_text=_("Set the starting bid for your product wisely"))
	end_date	= forms.DateField(help_text=_("When will the auction end?"))
	end_hour	= forms.ChoiceField(choices=HOUR_CHOICES, 
					help_text=_("What time will the auction end exactly?"))
	picture		= forms.ImageField(required=False, 
					help_text=_("Attract more eye balls with a sexy picture"))
