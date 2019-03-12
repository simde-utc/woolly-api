from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from core.helpers import gen_url_set, merge_sets
from woolly_api.settings import VIEWSET
from authentication.views import *
from .views import *


# JSON API Resource routes
urlpatterns = merge_sets(
	# User
	gen_url_set(['users', 'associations'], AssociationViewSet),
	gen_url_set(['users', 'orders'], OrderViewSet),

	# Association
	gen_url_set('associations', AssociationViewSet, AssociationRelationshipView),
	gen_url_set(['associations', 'sales'], SaleViewSet),
	# AssociationMember ????????????????????
	gen_url_set('associationmembers', AssociationMemberViewSet, AssociationMemberRelationshipView),
	gen_url_set(['associationmembers', 'associations'], AssociationViewSet),
	gen_url_set(['associations', 'associationmembers'], AssociationMemberViewSet),
	# Sale
	gen_url_set('sales', SaleViewSet, SaleRelationshipView),
	gen_url_set(['sales', 'associations'], AssociationViewSet),
	gen_url_set(['sales', 'items'], ItemViewSet),
	gen_url_set(['sales', 'itemgroups'], ItemGroupViewSet),
	gen_url_set(['sales', 'orders'], OrderViewSet),

	# ItemGroup
	gen_url_set('itemgroups', ItemGroupViewSet, ItemGroupRelationshipView),
	gen_url_set(['itemgroups', 'items'], ItemViewSet),
	# Item
	gen_url_set('items', ItemViewSet, ItemRelationshipView),
	gen_url_set(['items', 'fields'], FieldViewSet),
	gen_url_set(['items', 'sales'], SaleViewSet),
	gen_url_set(['items', 'itemgroups'], ItemGroupViewSet),
	gen_url_set(['items', 'usertypes'], UserTypeViewSet),
	gen_url_set(['items', 'itemfields'], ItemFieldViewSet, ItemFieldRelationshipView),

	# Order
	gen_url_set('orders', OrderViewSet, OrderRelationshipView),
	gen_url_set(['orders', 'sales'], SaleViewSet),
	gen_url_set(['orders', 'users'], UserViewSet),
	gen_url_set(['orders', 'orderlines'], OrderLineViewSet),
	# OrderLine
	gen_url_set('orderlines', OrderLineViewSet, OrderLineRelationshipView),
	gen_url_set(['orderlines', 'items'], ItemViewSet),
	gen_url_set(['orderlines', 'orders'], OrderViewSet),
	gen_url_set(['orderlines', 'orderlineitems'], OrderLineItemViewSet),
	# OrderLineItem ????
	gen_url_set('orderlineitems', OrderLineItemViewSet, OrderLineItemRelationshipView),
	gen_url_set(['orderlineitems', 'orderlines'], OrderLineViewSet),	
	gen_url_set(['orderlineitems', 'orderlinefields'], OrderLineFieldViewSet),	

	# Field
	gen_url_set('fields', FieldViewSet, FieldRelationshipView),
	gen_url_set(['fields', 'itemfields'], ItemFieldViewSet),
	# OrderLineField ?????????????????????
	gen_url_set('orderlinefields', OrderLineFieldViewSet, OrderLineFieldRelationshipView),
	gen_url_set(['orderlinefields', 'fields'], FieldViewSet),	
	# gen_url_set(['orderlinefield', 'orderline'], OrderLineViewSet),	
	gen_url_set(['orderlinefields', 'orderlineitems'], OrderLineItemViewSet),	
	# ItemField ??????????????????????
	gen_url_set('itemfields', ItemFieldViewSet, ItemFieldRelationshipView),
	gen_url_set(['itemfields', 'items'], ItemViewSet),
	gen_url_set(['itemfields', 'fields'], FieldViewSet),
)

# Addtionnal API endpoints for Authentication
urlpatterns += [
	# Generation du PDF
	url(r'^orders/(?P<order_pk>[0-9]+)/pdf/$', GeneratePdf.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
