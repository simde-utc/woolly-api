from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CreateOrderView, CreateItemView, ItemDetailsView, OrderDetailsView

urlpatterns = {
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^orders/$', CreateOrderView.as_view(), name="orders"),
    url(r'^items/$', CreateItemView.as_view(), name="items"),
    url(r'^items/(?P<pk>[0-9]+)/$',
        ItemDetailsView.as_view(), name="item-details"),
    url(r'^orders/(?P<pk>[0-9]+)/$',
        OrderDetailsView.as_view(), name="order-details"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
