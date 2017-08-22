from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from iauction.views import *

urlpatterns = patterns('',
    url(r'^$', iauction_home, name="iauction_home"),
    url(r'^booth/(?P<username>\w+)/$', iauction_booth, name="iauction_booth"),
    url(r'^sell/$', iauction_sell, name="iauction_sell"),
    url(r'^product/(?P<product_id>\d+)/$', iauction_product, name="iauction_product"),
    url(r'^bid/post/$', iauction_post_bid, name="iauction_post_bid"),
    url(r'^how/$', direct_to_template, {"template": "iauction/iauction_how.html"}, name="iauction_how"),
    url(r'^ajax/booth/products/(?P<username>\w+)/(?P<status>\w+)/$', 
		iauction_ajax_booth_products, name="iauction_ajax_booth_products"),
    url(r'^post/withdraw/$', iauction_post_withdraw, name="iauction_post_withdraw"),
    url(r'^post/confirm_delivery/$', iauction_post_confirm_delivery, name="iauction_post_confirm_delivery"),
    url(r'^post/confirm_receipt/$', iauction_post_confirm_receipt, name="iauction_post_confirm_receipt"),
)
