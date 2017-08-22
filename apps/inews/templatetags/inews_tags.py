from django import template
from django.conf import settings
register = template.Library()

@register.inclusion_tag("inews/post_tag.html")
def inews_post(post):
    return {"post": post,
        "MEDIA_URL": settings.MEDIA_URL,
    }

@register.tag
def inews_thumb_price(parser, token):
    """Provide the current price to thumb for the logged-in user."""
    try:
        tag_name, str_announcepost, str_user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return ThumbPriceNode(str_announcepost, str_user)

class ThumbPriceNode(template.Node):
    """Corresponds to thumb_price tag."""
    def __init__(self, str_announcepost, str_user):
        self.announcepost = template.Variable(str_announcepost)
        self.user = template.Variable(str_user)

    def render(self, context):
        try:
            announcepost = self.announcepost.resolve(context)
            user = self.user.resolve(context)
            return '{0}'.format(announcepost.get_next_thumb_price(user))
        except template.VariableDoesNotExist:
            return ''

