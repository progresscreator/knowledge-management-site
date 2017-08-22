from django import template
from django.conf import settings
register = template.Library()

@register.inclusion_tag("idesign/idea_tag.html")
def idesign_idea(idea):
	return {"idea": idea,
		"STATIC_URL": settings.STATIC_URL,
	}
