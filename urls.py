from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

from account.openid_consumer import PinaxConsumer
from blog.feeds import BlogFeedAll, BlogFeedUser
from bookmarks.feeds import BookmarkFeed
from microblogging.feeds import TweetFeedAll, TweetFeedUser, TweetFeedUserWithFriends
from iknow.feeds import QuestionFeedAll, QuestionFeedRewarding
from idoc.feeds import DocumentFeedAll
from egghead.views import bu2010spring, mit_bu_signup, french_signup

from django.contrib.sites.models import Site


tweets_feed_dict = {"feed_dict": {
    'all': TweetFeedAll,
    'only': TweetFeedUser,
    'with_friends': TweetFeedUserWithFriends,
}}

blogs_feed_dict = {"feed_dict": {
    'all': BlogFeedAll,
    'only': BlogFeedUser,
}}

bookmarks_feed_dict = {"feed_dict": { '': BookmarkFeed }}

questions_feed_dict = {"feed_dict": {
	"all": QuestionFeedAll,
	"rewarding": QuestionFeedRewarding,
}}

docs_feed_dict = {"feed_dict": {
	"all": DocumentFeedAll,
}}

if settings.ACCOUNT_OPEN_SIGNUP:
    signup_view = "account.views.signup"
else:
    signup_view = "signup_codes.views.signup"


homepage_template = "homepage.html"
current_site = Site.objects.get_current()
if current_site.domain.find("barter-dv.mit.edu") >= 0:
	homepage_template = "homepage-dv.html"
elif current_site.domain.find("barter.mit.edu") >= 0:
	homepage_template = "homepage-french.html"
else:
	homepage_template = "homepage.html"

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {
        "template": homepage_template,
    }, name="home"),
)
urlpatterns += patterns('',
    url(r'^admin/invite_user/$', 'signup_codes.views.admin_invite_user', name="admin_invite_user"),
    url(r'^account/signup/$', signup_view, name="acct_signup"),
    url(r'^account/signup/bu2010spring/$', bu2010spring, name="bu2010spring"),
    url(r'^account/signup/mit_bu_signup/$', mit_bu_signup, name="mit_bu_signup"),
    url(r'^account/signup/french/$', french_signup, name="french_signup"),
	url(r'^account/login/$', 'egghead.views.login', name="egghead_login"),
    
    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^bbauth/', include('bbauth.urls')),
    (r'^authsub/', include('authsub.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^blog/', include('blog.urls')),
    (r'^tags/', include('tag_app.urls')),
    (r'^invitations/', include('friends_app.urls')),
    (r'^notices/', include('notification.urls')),
    # (r'^messages/', include('messages.urls')),
    (r'^imessage/', include('imessage.urls')),
    (r'^announcements/', include('announcements.urls')),
    (r'^tweets/', include('microblogging.urls')),
    (r'^tribes/', include('tribes.urls')),
    (r'^comments/', include('threadedcomments.urls')),
    (r'^robots.txt$', include('robots.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^bookmarks/', include('bookmarks.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^photos/', include('photos.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^swaps/', include('swaps.urls')),
    (r'^flag/', include('flag.urls')),
    (r'^locations/', include('locations.urls')),
    
    (r'^feeds/tweets/(.*)/$', 'django.contrib.syndication.views.feed', tweets_feed_dict),
    (r'^feeds/posts/(.*)/$', 'django.contrib.syndication.views.feed', blogs_feed_dict),
    (r'^feeds/bookmarks/(.*)/?$', 'django.contrib.syndication.views.feed', bookmarks_feed_dict),

    (r'^feeds/questions/(.*)/$', 'django.contrib.syndication.views.feed', questions_feed_dict),
    (r'^feeds/documents/(.*)/?$', 'django.contrib.syndication.views.feed', docs_feed_dict),

    (r'^haystack/', include('haystack.urls')),
)

## @@@ for now, we'll use friends_app to glue this stuff together

from photos.models import Image

friends_photos_kwargs = {
    "template_name": "photos/friends_photos.html",
    "friends_objects_function": lambda users: Image.objects.filter(is_public=True, member__in=users),
}

from blog.models import Post

friends_blogs_kwargs = {
    "template_name": "blog/friends_posts.html",
    "friends_objects_function": lambda users: Post.objects.filter(author__in=users),
}

from microblogging.models import Tweet

friends_tweets_kwargs = {
    "template_name": "microblogging/friends_tweets.html",
    "friends_objects_function": lambda users: Tweet.objects.filter(sender_id__in=[user.id for user in users], sender_type__name='user'),
}

from bookmarks.models import Bookmark

friends_bookmarks_kwargs = {
    "template_name": "bookmarks/friends_bookmarks.html",
    "friends_objects_function": lambda users: Bookmark.objects.filter(saved_instances__user__in=users),
    "extra_context": {
        "user_bookmarks": lambda request: Bookmark.objects.filter(saved_instances__user=request.user),
    },
}

urlpatterns += patterns('',
    url('^photos/friends_photos/$', 'friends_app.views.friends_objects', kwargs=friends_photos_kwargs, name="friends_photos"),
    url('^blog/friends_blogs/$', 'friends_app.views.friends_objects', kwargs=friends_blogs_kwargs, name="friends_blogs"),
    url('^tweets/friends_tweets/$', 'friends_app.views.friends_objects', kwargs=friends_tweets_kwargs, name="friends_tweets"),
    url('^bookmarks/friends_bookmarks/$', 'friends_app.views.friends_objects', kwargs=friends_bookmarks_kwargs, name="friends_bookmarks"),
)


# Customized urls for barter
urlpatterns += patterns('',
    (r'^egghead/', include('egghead.urls')),
	(r'^iknow/', include('iknow.urls')),
	(r'^iquest/', include('iquest.urls')),
	(r'^idoc/', include('idoc.urls')),
        (r'^inews/', include('inews.urls')),
	(r'^iauction/', include('iauction.urls')),
	(r'^idea/', include('idea.urls')),
	(r'^idesign/', include('idesign.urls')),
	(r'^worldbank/', include('worldbank.urls')),
	(r'^dashboard/', include('dashboard.urls')),
	(r'^iap2010/', include('iap2010.urls')),
	(r'^barter/', include('core.urls')),
	(r'^facebook/', include('facebook.urls')),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('',
        (r'^site_media/', include('staticfiles.urls')),
    )
