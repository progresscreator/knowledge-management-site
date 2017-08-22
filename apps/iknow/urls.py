from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from iknow.views import *

urlpatterns = patterns('',
    url(r'^$', iknow_home, name="iknow_home"),
    url(r'^ask/$', iknow_ask, name="iknow_ask"),
    url(r'^myquestions/$', iknow_my_questions, name="iknow_my_questions"),
    url(r'^questions/$', iknow_questions, name="iknow_questions"),
    url(r'^question/(?P<question_id>\d+)/$', iknow_question, name="iknow_question"),
    url(r'^question_al/(?P<question_id>\d+)/$', iknow_question_al, name="iknow_question_al"),
    url(r'^answer/(?P<question_id>\d+)/$', iknow_answer, name="iknow_answer"),
	url(r'^help/$', iknow_help, name="iknow_help"),
    url(r'^tags/$', iknow_tags, name="iknow_tags"),
    url(r'^tag/(?P<tag_id>\d+)/$', iknow_tag, name="iknow_tag"),
    url(r'^dashboard/(?P<username>\w+)/$', iknow_dashboard, name="iknow_dashboard"),
)

# urls for ajax calls
urlpatterns += patterns('',
    url(r'^ajax/questions/(?P<qtype>\w+)/$', iknow_ajax_questions, name="iknow_ajax_questions"),
    url(r'^ajax/dashboard/(?P<username>\w+)/(?P<dtype>\w+)/$', iknow_ajax_dashboard, name="iknow_ajax_dashboard"),
    url(r'^question_extend/(?P<question_id>\d+)/$', iknow_question_extend, name="iknow_question_extend"),
    url(r'^question_moneyback/(?P<question_id>\d+)/$', iknow_question_moneyback, name="iknow_question_moneyback"),
    url(r'^ajax/suggested_questions/$', iknow_ajax_suggested_questions, name="iknow_ajax_suggested_questions"),
    url(r'^ajax/questions/(?P<qtype>\w+)/(?P<tribe_id>\d+)/$', iknow_ajax_questions, name="iknow_ajax_tribe_questions"),
    url(r'^ajax/questions/tags/(?P<qtype>\w+)/(?P<tag_id>\d+)/$', iknow_ajax_questions, name="iknow_ajax_tag_questions"),
    url(r'^question/comments/(?P<question_id>\d+)/$', iknow_ajax_question_comments, name="iknow_ajax_question_comments"),
)

# urls for posts
urlpatterns += patterns('',
    url(r'^post/thumbs/$', iknow_thumbs, name="iknow_thumbs"),
    url(r'^post/answerer_rating/$', iknow_answerer_rating, name="iknow_answerer_rating"),
    url(r'^post/tipping/$', iknow_tipping, name="iknow_tipping"),
    url(r'^post/comment/$', iknow_comment, name="iknow_comment"),
    url(r'^post/add/favorite/$', iknow_post_add_favorite, name="iknow_post_add_favorite"),
    url(r'^post/amendment/$', iknow_post_amendment, name="iknow_post_amendment"),
    url(r'^post/asker/hide/$', iknow_post_asker_hide, name="iknow_post_asker_hide"),
    url(r'^post/answerer/hide/$', iknow_post_answerer_hide, name="iknow_post_answerer_hide"),
)

# urls for json
urlpatterns += patterns('',
    url(r'^json/answer_comments/$', iknow_json_answer_comments, name="iknow_json_answer_comments"),
)

from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from iknow.models import Question
sqs = SearchQuerySet().models(Question)
# urls for search
urlpatterns += patterns('haystack.views',
	url(r'^search/$', SearchView(
		template="iknow/iknow_search.html",
		searchqueryset=sqs,
		form_class=ModelSearchForm
	), name="iknow_search"),
)
