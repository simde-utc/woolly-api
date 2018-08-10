from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url, include

from core.helpers import gen_url_set, merge_sets
from woolly_api.settings import VIEWSET
from authentication.views import *
from .views import *


# JSON API Resource routes
urlpatterns = merge_sets(
	# User
	gen_url_set(['user', 'association'], AssociationViewSet),
	gen_url_set(['user', 'order'], OrderViewSet),
	# Association
	gen_url_set('association', AssociationViewSet, AssociationRelationshipView),
	gen_url_set(['association', 'sale'], SaleViewSet),
	# Sale
	gen_url_set('sale', SaleViewSet, SaleRelationshipView),
	gen_url_set(['sale', 'item'], ItemViewSet),
	gen_url_set(['sale', 'itemgroup'], ItemGroupViewSet),
	gen_url_set(['sale', 'order'], OrderViewSet),
	# ItemGroup
	gen_url_set('itemgroup', ItemGroupViewSet, ItemGroupRelationshipView),
	gen_url_set(['itemgroup', 'item'], ItemViewSet),
	# Item
	gen_url_set('item', ItemViewSet, ItemRelationshipView),
	gen_url_set(['item', 'field'], FieldViewSet),
	gen_url_set(['item', 'sale'], SaleViewSet),
	gen_url_set(['item', 'itemgroup'], ItemGroupViewSet),
	gen_url_set(['item', 'usertype'], UserTypeViewSet),

	# Order
	gen_url_set('order', OrderViewSet, OrderRelationshipView),
	gen_url_set(['order', 'orderline'], OrderLineViewSet),
	# OrderLine
	gen_url_set('orderline', OrderLineViewSet, OrderLineRelationshipView),
	gen_url_set(['orderline', 'item'], ItemViewSet),
	gen_url_set(['orderline', 'orderlineitem'], OrderLineItemViewSet),
	# OrderLineItem
	gen_url_set('orderlineitem', OrderLineItemViewSet, OrderLineItemRelationshipView),
	# Field
	gen_url_set('field', FieldViewSet, FieldRelationshipView),
	# OrderLineField ?????????????????????
	gen_url_set('orderlinefield', OrderLineFieldViewSet, OrderLineFieldRelationshipView),
	gen_url_set(['orderlineitem', 'orderlinefield'], OrderLineFieldViewSet),
	# AssociationMember ????????????????????
	gen_url_set('associationmember', AssociationMemberViewSet, AssociationMemberRelationshipView),
	gen_url_set(['associationmember', 'association'], AssociationViewSet),
	gen_url_set(['association', 'associationmember'], AssociationMemberViewSet),
	# ItemField ??????????????????????
	gen_url_set('itemfield', ItemFieldViewSet, ItemFieldRelationshipView),
	gen_url_set(['item', 'itemfield'], ItemFieldViewSet, ItemFieldRelationshipView),
)

# Addtionnal API endpoints for Authentication
urlpatterns += [
	# Generation du PDF
	url(r'^orders/(?P<order_pk>[0-9]+)/pdf/$', GeneratePdf.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
