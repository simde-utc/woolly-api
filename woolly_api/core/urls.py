from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

# from .views import CreateOrderView, CreateItemView, ItemDetailsView, OrderDetailsView, CreateWoollyUserView

from core.views.orderLine import  OrderLineView
from core.views.itemGroup import CreateItemGroupView, ItemGroupDetailsView
from core.views.item import CreateItemView, ItemDetailsView
from core.views.order import CreateOrderView, OrderDetailsView

# API endpoints
urlpatterns = {
    url(r'^orders/$', CreateOrderView.as_view(), name="orders"),
    url(r'^items/$', CreateItemView.as_view(), name="items"),
    url(r'^lignes/$', OrderLineView.as_view(), name="orderLines"),
    url(r'^itemGroups/', CreateItemGroupView.as_view(), name="itemGroups"),
    url(r'^items/(?P<pk>[0-9]+)/$',
        ItemDetailsView.as_view(), name="item-detail"),
    url(r'^orders/(?P<pk>[0-9]+)/$',
        OrderDetailsView.as_view(), name="order-details"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
