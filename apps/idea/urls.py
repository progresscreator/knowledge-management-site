from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from idea.views import *

urlpatterns = patterns('',
    url(r'^$', idea_home, name="idea_home"),
    url(r'^coolidea/submit/$', idea_coolidea_submit, name="idea_coolidea_submit"),
    url(r'^coolidea/(?P<coolidea_id>\d+)/$', idea_coolidea, name="idea_coolidea"),
    url(r'^coolideas/$', idea_coolideas, name="idea_coolideas"),
    url(r'^post/thumbs/$', idea_post_thumbs, name="idea_post_thumbs"),
	url(r'^help/$', idea_help, name="idea_help"),
    url(r'^post/comment/thumbs/$', idea_post_comment_thumbs, name="idea_post_comment_thumbs"),
    url(r'^post/comment/tipping/$', idea_post_comment_tipping, name="idea_post_comment_tipping"),
    url(r'^post/rating/$', idea_post_rating, name="idea_post_rating"),
    url(r'^post/coolidea/comment/$', idea_post_coolidea_comment, name="idea_post_coolidea_comment"),
    url(r'^ajax/coolidea/comments/(?P<coolidea_id>\d+)/$', idea_ajax_coolidea_comments, 
		name="idea_ajax_coolidea_comments"),
)
# urls for search
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from idea.models import CoolIdea
sqs = SearchQuerySet().models(CoolIdea)
urlpatterns += patterns('haystack.views',
	url(r'^search/$', SearchView(
		template="idea/idea_search.html",
		searchqueryset=sqs,
		form_class=ModelSearchForm
	), name="idea_search"),
)
