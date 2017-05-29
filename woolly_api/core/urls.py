from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

# from .views import CreateOrderView, CreateItemView, ItemDetailsView, OrderDetailsView, CreateWoollyUserView
import cas.views

from core.views.orderLine import CreateOrderLineView, OrderLineDetailsView, OrderLineView
from core.views.itemGroup import CreateItemGroupView, ItemGroupDetailsView
from core.views.item import CreateItemView, ItemDetailsView
from core.views.order import CreateOrderView, OrderDetailsView
from core.views.woollyUser import CreateWoollyUserView

# API endpoints
urlpatterns = {
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^users/', CreateWoollyUserView.as_view(), name="users"),
    url(r'^orders/$', CreateOrderView.as_view(), name="orders"),
    url(r'^items/$', CreateItemView.as_view(), name="items"),
    url(r'^lignes/$', OrderLineView.as_view(), name="orderLines"),
    url(r'^itemGroups/', CreateItemGroupView.as_view(), name="itemGroups"),
    url(r'^items/(?P<pk>[0-9]+)/$',
        ItemDetailsView.as_view(), name="item-detail"),
    url(r'^orders/(?P<pk>[0-9]+)/$',
        OrderDetailsView.as_view(), name="order-details"),\
    url(r'^login/$', cas.views.login, name='login'),
    url(r'^logout/$', cas.views.logout, name='logout'),
}

urlpatterns = format_suffix_patterns(urlpatterns)
