from __future__ import unicode_literals

from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from mezzanine.conf import settings
from mezzanine.core.views import page_not_found

from ffcsa.core import views

_slash = "/" if settings.APPEND_SLASH else ""

urlpatterns = i18n_patterns(
    url("^$", views.shop_home, name="home"),
    url("^checkout%s$" % _slash, page_not_found, name="shop_checkout"),
    url("^checkout/complete%s$" % _slash, page_not_found,name="shop_complete"),
    url("^product/(?P<slug>.*)%s$" % _slash, views.product,name="shop_product"),
    url("^wishlist%s$" % _slash, page_not_found, name="shop_wishlist"),
)
