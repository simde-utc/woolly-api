from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path

from core.routing import merge_sets, gen_url_set
from authentication.views import UserViewSet, UserTypeViewSet
from .views import (
	AssociationViewSet, SaleViewSet, ItemGroupViewSet, ItemViewSet,
	OrderViewSet, OrderLineViewSet, OrderLineItemViewSet, FieldViewSet,
	OrderLineFieldViewSet, ItemFieldViewSet, generate_pdf
)

urlpatterns = merge_sets(
	# Association
	gen_url_set(AssociationViewSet),
	gen_url_set([AssociationViewSet, SaleViewSet]),
	gen_url_set([AssociationViewSet, UserViewSet]),

	# Sale
	gen_url_set(SaleViewSet),
	gen_url_set([SaleViewSet, AssociationViewSet]),
	gen_url_set([SaleViewSet, ItemViewSet]),
	gen_url_set([SaleViewSet, ItemGroupViewSet]),
	gen_url_set([SaleViewSet, OrderViewSet]),

	# ItemGroup
	gen_url_set(ItemGroupViewSet),
	gen_url_set([ItemGroupViewSet, ItemViewSet]),
	# Item
	gen_url_set(ItemViewSet),
	gen_url_set([ItemViewSet, FieldViewSet]),
	gen_url_set([ItemViewSet, SaleViewSet]),
	gen_url_set([ItemViewSet, ItemGroupViewSet]),
	gen_url_set([ItemViewSet, UserTypeViewSet]),
	gen_url_set([ItemViewSet, ItemFieldViewSet]),

	# Order
	gen_url_set(OrderViewSet),
	gen_url_set([OrderViewSet, SaleViewSet]),
	gen_url_set([OrderViewSet, UserViewSet]),
	gen_url_set([OrderViewSet, OrderLineViewSet]),
	# OrderLine
	gen_url_set(OrderLineViewSet),
	gen_url_set([OrderLineViewSet, ItemViewSet]),
	gen_url_set([OrderLineViewSet, OrderViewSet]),
	gen_url_set([OrderLineViewSet, OrderLineItemViewSet]),
	# OrderLineItem
	gen_url_set(OrderLineItemViewSet),
	gen_url_set([OrderLineItemViewSet, OrderLineViewSet]),
	gen_url_set([OrderLineItemViewSet, OrderLineFieldViewSet]),

	# Field
	gen_url_set(FieldViewSet),
	gen_url_set([FieldViewSet, ItemFieldViewSet]),
	# OrderLineField
	gen_url_set(OrderLineFieldViewSet),
	gen_url_set([OrderLineFieldViewSet, FieldViewSet]),
	gen_url_set([OrderLineFieldViewSet, OrderLineItemViewSet]),
	# ItemField
	gen_url_set(ItemFieldViewSet),
	gen_url_set([ItemFieldViewSet, ItemViewSet]),
	gen_url_set([ItemFieldViewSet, FieldViewSet]),
)

urlpatterns += [
	# Generation du PDF
	path('orders/<int:pk>/pdf', generate_pdf),
]


urlpatterns = format_suffix_patterns(urlpatterns)
