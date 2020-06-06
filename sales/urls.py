from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from core.routing import merge_sets, gen_url_set
from authentication.views import UserViewSet, UserTypeViewSet
from .views import (
    AssociationViewSet, SaleViewSet, ItemGroupViewSet, ItemViewSet,
    OrderViewSet, OrderLineViewSet, OrderLineItemViewSet, FieldViewSet,
    OrderLineFieldViewSet, ItemFieldViewSet, generate_tickets
)

urlpatterns = merge_sets(
    # Associations
    gen_url_set(AssociationViewSet),
    gen_url_set([AssociationViewSet, SaleViewSet]),
    gen_url_set([AssociationViewSet, UserViewSet]),

    # Sales
    gen_url_set(SaleViewSet),
    gen_url_set([SaleViewSet, AssociationViewSet]),
    gen_url_set([SaleViewSet, ItemViewSet]),
    gen_url_set([SaleViewSet, ItemGroupViewSet]),
    gen_url_set([SaleViewSet, OrderViewSet]),
    gen_url_set([SaleViewSet, OrderLineViewSet]),

    # ItemGroups
    gen_url_set(ItemGroupViewSet),
    gen_url_set([ItemGroupViewSet, ItemViewSet]),
    # Items
    gen_url_set(ItemViewSet),
    gen_url_set([ItemViewSet, FieldViewSet]),
    gen_url_set([ItemViewSet, SaleViewSet]),
    gen_url_set([ItemViewSet, ItemGroupViewSet]),
    gen_url_set([ItemViewSet, UserTypeViewSet]),
    gen_url_set([ItemViewSet, ItemFieldViewSet]),

    # Orders
    gen_url_set(OrderViewSet),
    gen_url_set([OrderViewSet, SaleViewSet]),
    gen_url_set([OrderViewSet, UserViewSet]),
    gen_url_set([OrderViewSet, OrderLineViewSet]),
    # OrderLines
    gen_url_set(OrderLineViewSet),
    gen_url_set([OrderLineViewSet, ItemViewSet]),
    gen_url_set([OrderLineViewSet, OrderViewSet]),
    gen_url_set([OrderLineViewSet, OrderLineItemViewSet]),
    # OrderLineItems
    gen_url_set(OrderLineItemViewSet),
    gen_url_set([OrderLineItemViewSet, OrderLineViewSet]),
    gen_url_set([OrderLineItemViewSet, OrderLineFieldViewSet]),

    # Fields
    gen_url_set(FieldViewSet),
    gen_url_set([FieldViewSet, ItemFieldViewSet]),
    # ItemFields
    gen_url_set(ItemFieldViewSet),
    gen_url_set([ItemFieldViewSet, ItemViewSet]),
    gen_url_set([ItemFieldViewSet, FieldViewSet]),
    # OrderLineFields
    gen_url_set(OrderLineFieldViewSet),
    gen_url_set([OrderLineFieldViewSet, FieldViewSet]),
    gen_url_set([OrderLineFieldViewSet, OrderLineItemViewSet]),
)

urlpatterns += [
    # Generation du PDF
    path('orders/<int:pk>/pdf', generate_tickets),
]


urlpatterns = format_suffix_patterns(urlpatterns)
