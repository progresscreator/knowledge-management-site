# -*- coding: utf-8 -*-
# Django settings for social pinax project.

import os.path
import posixpath
import pinax
import os
import logging
import logging.handlers

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = DEBUG

ADMINS = (
	('Dawei Shen', 'dawei@media.mit.edu'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'knowledge.db'       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
	
# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
# USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/media/'

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = '/site_media/static/'

# Additional directories which hold static files
STATICFILES_DIRS = (
    ('knowledge_web', os.path.join(PROJECT_ROOT, 'media')),
    ('pinax', os.path.join(PINAX_ROOT, 'media', PINAX_THEME)),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = posixpath.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm46y_@6y$lgso921u+m02f-7%&1q7wg-$fk&_*=aq&$i6v(!v*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
    'pinax.middleware.security.HideSensistiveFieldsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'knowledge_web.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    
    "pinax.core.context_processors.pinax_settings",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
    "account.context_processors.openid",
    "account.context_processors.account",
    "imessage.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "knowledge_web.context_processors.combined_inbox_count",
    "knowledge_web.context_processors.current_site_name",
)

COMBINED_INBOX_COUNT_SOURCES = (
    "imessage.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "notification.context_processors.notification",
)

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'pinax.templatetags',
    
    # external
    'notification', # must be first
    'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    'friends',
    'mailer',
    'imessage',
    'announcements',
    'oembed',
    # 'djangodblog',
    'pagination',
#    'gravatar',
    'threadedcomments',
    'threadedcomments_extras',
    # 'wiki',
    # 'swaps',
    'timezones',
    'voting',
    'voting_extras',
    'tagging',
    'bookmarks',
    # 'blog',
    'ajax_validation',
    'photologue',
    'avatar',
    'flag',
    # 'microblogging',
    'locations',
    'uni_form',
    'django_sorting',
    'django_markup',
    'staticfiles',
    
    # internal (for now)
    'analytics',
    'profiles',
    'account',
    'signup_codes',
    'tribes',
    'photos',
    'tag_app',
    'topics',
    'groups',
    
    'django.contrib.admin',

	'sorl.thumbnail',
    # my own apps for barter
	'core',
    'egghead',
    'iknow',
    'iquest',
    'iauction',
    'idea',
    'idesign',
    'inews',
    'mysearch',
    'haystack',
    'idoc',
    'worldbank',
    'dashboard',
	'iap2010',
	'facebook',
)

HAYSTACK_SITECONF = 'mysearch.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = "/var/tmp/whoosh_index"
	

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

MARKUP_FILTER_FALLBACK = 'none'
MARKUP_CHOICES = (
    ('restructuredtext', u'reStructuredText'),
    ('textile', u'Textile'),
    ('markdown', u'Markdown'),
    ('creole', u'Creole'),
)
WIKI_MARKUP_CHOICES = MARKUP_CHOICES

AUTH_PROFILE_MODULE = 'profiles.Profile'
NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

# Is registration allowed
ACCOUNT_OPEN_SIGNUP = False
ACCOUNT_REQUIRED_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = True

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "dawei@media.mit.edu"
SITE_NAME = "Barter"
site_name = "Barter"
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URLNAME = "what_next"

INTERNAL_IPS = (
    '127.0.0.1',
)


LOG_FILE = os.path.join(PROJECT_ROOT, "log", "knowledge.log")
if not os.path.exists(os.path.join(PROJECT_ROOT, "log")):
	os.mkdir(os.path.join(PROJECT_ROOT, "log"))
LOGGER_SETUP = False
if not LOGGER_SETUP:
	klogger = logging.getLogger("pwe")
	klogger.setLevel(logging.DEBUG)
	khandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=20e6, backupCount=5)
	khandler.setLevel(logging.DEBUG)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
		'%a, %d %b %Y %H:%M:%S')
	khandler.setFormatter(formatter)
	klogger.addHandler(khandler)
	LOGGER_SETUP = True


ugettext = lambda s: s
LANGUAGES = (
    ('en', u'English'),
    ('fr', u'French'),
    ('ru', u'Russian'),
)

# URCHIN_ID = "ua-..."

YAHOO_MAPS_API_KEY = "..."

class NullStream(object):
    def write(*args, **kwargs):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'cloak_email_addresses': True,
    'file_insertion_enabled': False,
    'raw_enabled': False,
    'warning_stream': NullStream(),
    'strip_comments': True,
}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True

# Uncomment this line after signing up for a Yahoo Maps API key at the
# following URL: https://developer.yahoo.com/wsregapp/
# YAHOO_MAPS_API_KEY = ''

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
