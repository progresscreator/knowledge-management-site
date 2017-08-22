from django import template
from django.conf import settings
register = template.Library()

@register.inclusion_tag("idea/coolidea_tag.html")
def idea_coolidea(coolidea):
	return {"coolidea": coolidea,
		"STATIC_URL": settings.STATIC_URL,
	}
