from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

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
        OrderDetailsView.as_view(), name="order-detail"),
    url(r'^orders/(?P<pk>[0-9]+)/cart/$',
        CreateOrderLineView.as_view(), name="cart-detail"),
    url(r'^lignes/(?P<pk>[0-9]+)/$',
        OrderLineDetailsView.as_view(), name="orderLine-detail"),
    url(r'^itemGroups/(?P<pk>[0-9]+)/$',
        ItemGroupDetailsView.as_view(), name="itemGroup-detail"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
