from django import template
from django.conf import settings
register = template.Library()

@register.inclusion_tag("iknow/iknow_tag_question_icon.html")
def question_icon(question):
	return {"question": question,
		"STATIC_URL": settings.STATIC_URL,
	}
