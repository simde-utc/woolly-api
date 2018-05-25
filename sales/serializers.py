from .models import (Association, AssociationMember, PaymentMethod, Sale, Order, ItemGroup, Item, 
					OrderLine, Field, ItemField, OrderLineField)
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from authentication.models import User, UserType
from authentication.serializers import UserSerializer, UserTypeSerializer


# ============================================
# 	Payment, Items & Sales
# ============================================

class PaymentMethodSerializer(serializers.ModelSerializer):
	"""
	Defines how the PaymentMethod fields are serialized
	"""
	"""
	sales = ResourceRelatedField(
		queryset=Sale.objects,
		many=True,
		related_link_view_name='sale-payment-list',
		related_link_url_kwarg='payment_pk',
		self_link_view_name='paymentmethod-relationships'
	)

	included_serializers = {
		'sales': SaleSerializer
	}
	"""
	class Meta:
		model = PaymentMethod
		# fields = ('id', 'name', 'api_url', 'sales')

	class JSONAPIMeta:
		pass
		# included_resources = ['sales']

class ItemSerializer(serializers.ModelSerializer):
	"""
	Defines how the Item fields are serialized
	"""
	
	class Meta:
		model = Item
		# fields = ('id', 'name', 'description', 'remaining_quantity',
				  # 'initial_quantity','sale_id', 'itemspecifications')

	class JSONAPIMeta:
		# included_resources = ['itemspecifications']
		pass


class SaleSerializer(serializers.ModelSerializer):
	"""
	Defines how the Sale fields are serialized, without the payment methods
	"""
	association = serializers.ReadOnlyField(source='association.name')
	items = ResourceRelatedField(
		queryset = Item.objects,
		many = True,
		related_link_view_name = 'item-list',
		related_link_url_kwarg = 'sale_pk',
		self_link_view_name = 'sale-relationships'
	)

	included_serializers = {
		'items': ItemSerializer,
		'paymentmethods': PaymentMethodSerializer

	}

	class Meta:
		model = Sale
		# fields = ('id', 'name', 'description', 'creation_date', 'begin_date',
				  # 'end_date', 'max_payment_date', 'max_item_quantity', 'association', 'items')

	class JSONAPIMeta:
		included_resources = ['items', 'paymentmethods']



# ============================================
# 	Associations
# ============================================

class AssociationSerializer(serializers.ModelSerializer):
	"""
	Defines how the Association fields are serialized
	"""
	sales = ResourceRelatedField(
		queryset = Sale.objects,
		many = True,
		related_link_view_name = 'sale-list',
		related_link_url_kwarg = 'association_pk',
		self_link_view_name = 'association-relationships'
	)

	included_serializers = {
		'sales': SaleSerializer
	}

	class Meta:
		model = Association
		fields = ('id', 'name', 'bank_account', 'sales', 'foundation_id')

	class JSONAPIMeta:
		included_resources = ['sales']

class AssociationMemberSerializer(serializers.ModelSerializer):
	"""
	Defines how the AssociationMember fields are serialized
	"""
	association = ResourceRelatedField(
		queryset = Association.objects,
		related_link_view_name = 'association-list',
		related_link_url_kwarg = 'associationmember_pk',
		self_link_view_name = 'associationmember-relationships'
	)
	user = ResourceRelatedField(
		queryset = User.objects,
		related_link_view_name = 'association-list',
		related_link_url_kwarg = 'associationmember_pk',
		self_link_view_name = 'associationmember-relationships'
	)

	included_serializers = {
		'association': AssociationSerializer,
		'user': UserSerializer,
	}

	class Meta:
		model = AssociationMember
		# fields = ('id', 'association', 'role', 'rights')

	class JSONAPIMeta:
		included_resources = ['association', 'user']

# ============================================
# 	Orders
# ============================================

class OrderLineSerializer(serializers.ModelSerializer):
	"""
	Defines how the OrderLine fields are serialized
	"""
	order = serializers.ReadOnlyField(source='order.id')
	print('******************************')
	
	item = ResourceRelatedField(
		queryset=Item.objects,
		related_link_view_name='orderlineitem-list',
		related_link_url_kwarg='orderline_pk',
		self_link_view_name='orderline-relationships'
	)

	included_serializers = {
		'item': ItemSerializer,
	}

	class Meta:
		model = OrderLine
		fields = ('id', 'order', 'item', 'quantity')

	class JSONAPIMeta:
		included_resources = ['item']


class OrderSerializer(serializers.ModelSerializer):
	"""
	Defines how the Order fields are serialized
	"""
	orderlines = ResourceRelatedField(
		queryset=OrderLine.objects,
		many=True,
		related_link_view_name='orderline-list',
		related_link_url_kwarg='order_pk',
		self_link_view_name='order-relationships'
	)
	# sale = serializers.ReadOnlyField(source='orderlines.item.sale')
	included_serializers = {
		'orderlines': OrderLineSerializer,
	}

	class Meta:
		model = Order
		fields = ('id', 'date','price','hash_key', 'orderlines')

	class JSONAPIMeta:
		included_resources = ['orderlines']


