from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from dashboard.views import *

urlpatterns = patterns('',
    url(r'^home/(?P<username>\w+)/$', db_home,  name="db_home"),
    url(r'^tags/$', db_tags,  name="db_tags"),
    url(r'^global/$', db_global,  name="db_global"),
    url(r'^expertise/$', db_expertise,  name="db_expertise"),
    url(r'^expertise/json/$', db_json_expertise,  name="db_json_expertise"),
    url(r'^qa_social/(?P<username>\w+)/$', db_social,  name="db_social"),
    url(r'^qa_social_slab_serif/(?P<username>\w+)/$', db_social_slab_serif,  name="db_social_slab_serif"),
    url(r'^qa_social_verdana/(?P<username>\w+)/$', db_social_verdana,  name="db_social_verdana"),
    url(r'^qa_social_arial/(?P<username>\w+)/$', db_social_arial,  name="db_social_arial"),
    url(r'^qa_social_alter_color/(?P<username>\w+)/$', db_social_alter_color,  name="db_social_alter_color"),
    url(r'^qa_social/json/network/(?P<username>\w+)/$', db_social_json_network, name="db_social_json_network"),

    url(r'^vis/json/income_pie/$', vis_json_income_pie, name="vis_json_income_pie"),
    url(r'^vis/json/inout_pie/$', vis_json_inout_pie, name="vis_json_inout_pie"),
    url(r'^vis/json/answer/rating/(?P<username>\w+)/$', vis_json_answer_rating, name="vis_json_answer_rating"),
    url(r'^vis/json/answer/thumbs/(?P<username>\w+)/$', vis_json_answer_thumbs, name="vis_json_answer_thumbs"),
    url(r'^vis/json/answer/award/(?P<username>\w+)/$', vis_json_answer_award, name="vis_json_answer_award"),
    url(r'^vis/json/time_series/(?P<username>\w+)/$', vis_json_time_series, name="vis_json_time_series"),

    url(r'^vis/json/tag_cloud/$', vis_json_tag_cloud, name="vis_json_tag_cloud"),
    url(r'^vis/json/tag_cloud_news/$', vis_json_tag_cloud_news, name="vis_json_tag_cloud_news"),

    url(r'^vis/json/tag_cloud/(?P<username>\w+)/$', vis_json_tag_cloud_user, name="vis_json_tag_cloud_user"),

    url(r'^vis/json/qa_vis/$', vis_json_qa_vis, name="vis_json_qa_vis"),
    url(r'^vis/json/qa_price_vis/$', vis_json_qa_price_vis, name="vis_json_qa_price_vis"),
    url(r'^vis/json/transactions_vis/$', vis_json_transactions_vis, name="vis_json_transactions_vis"),

    url(r'^vis/json/dist_wealth/$', vis_json_dist_wealth, name="vis_json_dist_wealth"),
    url(r'^vis/json/dist_earnings/$', vis_json_dist_earnings, name="vis_json_dist_earnings"),
    url(r'^vis/json/market_pie/$', vis_json_market_pie, name="vis_json_market_pie"),
    url(r'^vis/json/type_pie/$', vis_json_type_pie, name="vis_json_type_pie"),

    url(r'^expertise_slab_serif/$', db_expertise_slab_serif,  name="db_expertise_slab_serif"),
    url(r'^expertise_verdana/$', db_expertise_verdana,  name="db_expertise_verdana"),
    url(r'^expertise_arial/$', db_expertise_arial,  name="db_expertise_arial"),
    url(r'^expertise_alter_color/$', db_expertise_alter_color,  name="db_expertise_alter_color"),
)
