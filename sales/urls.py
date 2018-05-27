from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from woolly_api.settings import VIEWSET
from .views import *

# Configure Viewsets
association_list   = AssociationViewSet.as_view(VIEWSET['list'])
association_detail = AssociationViewSet.as_view(VIEWSET['detail'])

associationmember_list   = AssociationMemberViewSet.as_view(VIEWSET['list'])
associationmember_detail = AssociationMemberViewSet.as_view(VIEWSET['detail'])

sale_list   = SaleViewSet.as_view(VIEWSET['list'])
sale_detail = SaleViewSet.as_view(VIEWSET['detail'])

itemgroup_list   = ItemGroupViewSet.as_view(VIEWSET['list'])
itemgroup_detail = ItemGroupViewSet.as_view(VIEWSET['detail'])

item_list   = ItemViewSet.as_view(VIEWSET['list'])
item_detail = ItemViewSet.as_view(VIEWSET['detail'])

order_list   = OrderViewSet.as_view(VIEWSET['list'])
order_detail = OrderViewSet.as_view(VIEWSET['detail'])

orderline_list   = OrderLineViewSet.as_view(VIEWSET['list'])
orderline_detail = OrderLineViewSet.as_view(VIEWSET['detail'])

field_list   = FieldViewSet.as_view(VIEWSET['list'])
field_detail = FieldViewSet.as_view(VIEWSET['detail'])

itemfield_list   = ItemFieldViewSet.as_view(VIEWSET['list'])
itemfield_detail = ItemFieldViewSet.as_view(VIEWSET['detail'])

orderlinefield_list   = OrderLineFieldViewSet.as_view(VIEWSET['list'])
orderlinefield_detail = OrderLineFieldViewSet.as_view(VIEWSET['detail'])

paymentmethod_list   = PaymentMethodViewSet.as_view(VIEWSET['list'])
paymentmethod_detail = PaymentMethodViewSet.as_view(VIEWSET['detail'])



# The urlpatterns defines the endpoints of the API
urlpatterns = [

	# ============================================
	# 	Association
	# ============================================
	url(r'^associations$',
		view = association_list, name = 'association-list'),
	url(r'^associations/(?P<pk>[0-9]+)$',
		view = association_detail, name = 'association-detail'),
	url(r'^associations/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = AssociationRelationshipView.as_view(), name = 'association-relationships'),

	# Assos from Users
	url(r'^users/(?P<user_pk>[0-9]+)/associations$',
		view = association_list, name = 'association-list'),
	url(r'^users/(?P<user_pk>[0-9]+)/associations/(?P<pk>[0-9]+)$',
		view = association_detail, name = 'association-detail'),

	# Members from Assos
	url(r'^associations/(?P<association_pk>[0-9]+)/associationmembers$',
		view = associationmember_list, name = 'associationmember-list'),
	url(r'^associations/(?P<association_pk>[0-9]+)/associationmembers/(?P<pk>[0-9]+)$',
		view = associationmember_detail, name = 'associationmember-list'),

	# Members : TODO UTILE ?
	url(r'^associationmembers$',
		view = associationmember_list, name = 'associationmember-list'),
	url(r'^associationmembers/(?P<pk>[0-9]+)$',
		view = associationmember_detail, name = 'associationmember-detail'),
	url(r'^associationmembers/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = AssociationMemberRelationshipView.as_view(), name = 'associationmember-relationships'),

	# Assos from Members: TODO UTILE ?
	url(r'^associationmembers/(?P<associationmember_pk>[0-9]+)/associations$',
		view = association_list, name = 'association-list'),
	url(r'^associationmembers/(?P<associationmember_pk>[0-9]+)/associations/(?P<pk>[0-9]+)$',
		view = association_detail, name = 'association-detail'),


	# ============================================
	# 	Sale
	# ============================================
	url(r'^sales$',
		view = sale_list, name = 'sale-list'),
	url(r'^sales/(?P<pk>[0-9]+)$',
		view = sale_detail, name = 'sale-detail'),
	url(r'^sales/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = SaleRelationshipView.as_view(), name = 'sale-relationships'),

	# From Assos
	url(r'^associations/(?P<association_pk>[0-9]+)/sales$',
		view = sale_list, name = 'sale-list'),
	url(r'^associations/(?P<association_pk>[0-9]+)/sales/(?P<pk>[0-9]+)$',
		view = sale_detail, name = 'sale-detail'),


	# ============================================
	# 	ItemGroup
	# ============================================
	url(r'^itemgroups$',
		view = itemgroup_list, name = 'itemgroup-list'),
	url(r'^itemgroups/(?P<pk>[0-9]+)$',
		view = itemgroup_detail, name = 'itemgroup-detail'),
	url(r'^itemgroups/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = ItemGroupRelationshipView.as_view(), name = 'item-relationships'),

	# From Sale
	url(r'^sales/(?P<sale_pk>[0-9]+)/itemgroups$',
		view = itemgroup_list, name = 'itemgroup-list'),
	url(r'^sales/(?P<sale_pk>[0-9]+)/itemgroups/(?P<pk>[0-9]+)$',
		view = itemgroup_detail, name = 'itemgroup-detail'),


	# ============================================
	# 	Item
	# ============================================
	url(r'^items$',
		view = item_list, name = 'item-list'),
	url(r'^items/(?P<pk>[0-9]+)$',
		view = item_detail, name = 'item-detail'),
	url(r'^items/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = ItemRelationshipView.as_view(), name = 'item-relationships'),

	# From ItemGroup
	url(r'^itemgroups/(?P<item_pk>[0-9]+)/items$',
		view = item_list, name = 'item-list'),
	url(r'^itemgroups/(?P<item_pk>[0-9]+)/items/(?P<pk>[0-9]+)$',
		view = item_detail, name = 'item-detail'),

	# From Sales
	url(r'^sales/(?P<sale_pk>[0-9]+)/items$',
		view = item_list, name = 'item-list'),
	url(r'^sales/(?P<sale_pk>[0-9]+)/items/(?P<pk>[0-9]+)$',
		view = item_detail, name = 'item-detail'),

	# From Assos > Sales
	url(r'^associations/(?P<association_pk>[0-9]+)/sales/(?P<sale_pk>[0-9]+)/items$',
		view = item_list, name = 'item-list'),
	url(r'^associations/(?P<association_pk>[0-9]+)/sales/(?P<sale_pk>[0-9]+)/items/(?P<pk>[0-9]+)$',
		view = item_detail, name = 'item-detail'),

	# From OrderLines
	url(r'^orderlines/(?P<orderline_pk>[0-9]+)/items$',
		view = item_list, name = 'orderline-list'),
	url(r'^orderlines/(?P<orderline_pk>[0-9]+)/items/(?P<pk>[0-9]+)$',
		view = item_detail, name = 'orderline-detail'),


	# ============================================
	# 	Order
	# ============================================
	url(r'^orders$',
		view = order_list, name = 'order-list'),
	url(r'^orders/(?P<pk>[0-9]+)$',
		view = order_detail, name = 'order-detail'),
	url(r'^orders/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = OrderRelationshipView.as_view(), name = 'order-relationships'),

	# From Users
	url(r'^users/(?P<user_pk>[0-9]+)/orders$',
		view = order_list, name = 'order-list'),
	url(r'^users/(?P<user_pk>[0-9]+)/orders/(?P<pk>[0-9]+)$',
		view = order_detail, name = 'order-detail'),

	# From Sales
	url(r'^sales/(?P<sale_pk>[0-9]+)/orders$',
		view = order_list, name = 'order-list'),
	url(r'^sales/(?P<sale_pk>[0-9]+)/orders/(?P<pk>[0-9]+)$',
		view = order_detail, name = 'order-detail'),


	# ============================================
	# 	OrderLine
	# ============================================
	url(r'^orderlines$',
		view = orderline_list, name = 'orderline-list'),
	url(r'^orderlines/(?P<pk>[0-9]+)$',
		view = orderline_detail, name = 'orderline-detail'),
	url(r'^orderlines/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = OrderLineRelationshipView.as_view(), name = 'orderline-relationships'),

	# From Orders
	url(r'^orders/(?P<order_pk>[0-9]+)/orderlines$',
		view = orderline_list, name = 'orderline-list'),
	url(r'^orders/(?P<order_pk>[0-9]+)/orderlines/(?P<pk>[0-9]+)$',
		view = orderline_detail, name = 'orderline-detail'),


	# ============================================
	# 	Field
	# ============================================
	url(r'^fields$',
		view = field_list, name = 'field-list'),
	url(r'^fields/(?P<pk>[0-9]+)$',
		view = field_detail, name = 'field-detail'),
	url(r'^fields/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = FieldRelationshipView.as_view(), name = 'field-relationships'),

	# From Items
	url(r'^items/(?P<item_pk>[0-9]+)/fields$',
		view = field_list, name = 'field-list'),
	url(r'^items/(?P<item_pk>[0-9]+)/fields/(?P<pk>[0-9]+)$',
		view = orderline_detail, name = 'orderline-detail'),


	# ============================================
	# 	ItemField : INUTILE ????
	# ============================================
	url(r'^itemfields$',
		view = itemfield_list, name = 'itemfield-list'),
	url(r'^itemfields/(?P<pk>[0-9]+)$',
		view = itemfield_detail, name = 'itemfield-detail'),
	url(r'^itemfields/(?P<pk>[^/.]+)/relationships/(?P<related_itemfield>[^/.]+)$',
		view = ItemFieldRelationshipView.as_view(), name = 'itemfield-relationships'),

	# From Items
	url(r'^items/(?P<item_pk>[0-9]+)/itemfields$',
		view = itemfield_list, name = 'itemfield-list'),
	url(r'^items/(?P<item_pk>[0-9]+)/itemfields/(?P<pk>[0-9]+)$',
		view = orderline_detail, name = 'itemfields-detail'),


	# ============================================
	# 	OrderLineItemField : INUTILE ???
	# ============================================
	url(r'^orderlinefields$',
		view = orderlinefield_list, name = 'orderlinefield-list'),
	url(r'^orderlinefields/(?P<pk>[0-9]+)$',
		view = orderlinefield_detail, name = 'orderlinefield-detail'),
	url(r'^orderlinefields/(?P<pk>[^/.]+)/relationships/(?P<related_orderlinefield>[^/.]+)$',
		view = OrderLineFieldRelationshipView.as_view(), name = 'orderlinefield-relationships'),

	# From Orderlines
	url(r'^orderlines/(?P<orderline_pk>[0-9]+)/orderlinefields$',
		view = orderlinefield_list, name = 'orderlinefield-list'),
	url(r'^orderlines/(?P<orderline_pk>[0-9]+)/orderlinefields/(?P<pk>[0-9]+)$',
		view = orderline_detail, name = 'orderlinefields-detail'),





	# ============================================
	# 	Payment Methods : A VIRER
	# ============================================
	url(r'^paymentmethods$',
		view = paymentmethod_list, name = 'paymentmethod-list'),
	url(r'^paymentmethods/(?P<pk>[0-9]+)$',
		view = paymentmethod_detail, name = 'paymentmethod-detail'),
	url(r'^paymentmethods/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = PaymentMethodRelationshipView.as_view(), name = 'paymentmethod-relationships'),

	url(r'^sales/(?P<sale_pk>[0-9]+)/paymentmethods$',
		view = paymentmethod_list, name = 'paymentmethod-list'),
	url(r'^sales/(?P<sale_pk>[0-9]+)/paymentmethods/(?P<pk>[0-9]+)$',
		view = paymentmethod_detail, name = 'paymentmethod-detail'),
	url(r'^paymentmethods/(?P<payment_pk>[0-9]+)/sales$',
		view = sale_list, name = 'sale-payment-list'),
	url(r'^paymentmethods/(?P<payment_pk>[0-9]+)/sales/(?P<pk>[0-9]+)$',
		view = sale_detail, name = 'sale-payment-detail'),

]
