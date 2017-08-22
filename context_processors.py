from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from microblogging.models import Tweet
from tribes.models import Tribe
from bookmarks.models import Bookmark
from blog.models import Post

_inbox_count_sources = None

def inbox_count_sources():
    global _inbox_count_sources
    if _inbox_count_sources is None:
        sources = []
        for path in settings.COMBINED_INBOX_COUNT_SOURCES:
            i = path.rfind('.')
            module, attr = path[:i], path[i+1:]
            try:
                mod = __import__(module, {}, {}, [attr])
            except ImportError, e:
                raise ImproperlyConfigured('Error importing request processor module %s: "%s"' % (module, e))
            try:
                func = getattr(mod, attr)
            except AttributeError:
                raise ImproperlyConfigured('Module "%s" does not define a "%s" callable request processor' % (module, attr))
            sources.append(func)
        _inbox_count_sources = tuple(sources)
    return _inbox_count_sources

def combined_inbox_count(request):
    """
    A context processor that uses other context processors defined in
    setting.COMBINED_INBOX_COUNT_SOURCES to return the combined number from
    arbitrary counter sources.
    """
    count = 0
    for func in inbox_count_sources():
        counts = func(request)
        if counts:
            for value in counts.itervalues():
                try:
                    count = count + int(value)
                except (TypeError, ValueError):
                    pass
    return {'combined_inbox_count': count,}

def footer(request):
    return {
        'latest_tweets': Tweet.objects.all().order_by('-sent')[:5],
        'latest_tribes': Tribe.objects.all().order_by('-created')[:5],
        'latest_users': User.objects.all().order_by('-date_joined')[:9],
        'latest_bookmarks': Bookmark.objects.all().order_by('-added')[:5],
        'latest_blogs': Post.objects.filter(status=2).order_by('-publish')[:5],
    }

def current_site_name(request):
	current_site = Site.objects.get_current()
	site_name = "debug"
	if current_site.domain.find("barter-dv.mit.edu") >= 0:
		site_name = "barter-dv"
	elif current_site.domain.find("barter.mit.edu") >= 0:
		site_name = "barter"
	elif current_site.domain.find("figaro.mit.edu") >= 0:
		site_name = "figaro"
	elif current_site.domain.find("iknow.mit.edu") >= 0:
		site_name = "iknow"
	elif current_site.domain.find("nomadlab.mit.edu") >= 0:
		site_name = "nomadlab"
	# site_name = "barter-dv"
	hide_idesign = site_name in ()
	facebook_enabled = site_name in ("figaro", "iknow")
	inews_enabled = site_name in ("iknow", "debug")
	imessage_enabled = site_name in ("iknow", "debug")
	return {"current_site_name": site_name,
			"hide_idesign": hide_idesign,
			"facebook_enabled": facebook_enabled,
			"inews_enabled": inews_enabled,
			"imessage_enabled": imessage_enabled,
			}
