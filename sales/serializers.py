from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from authentication.models import User, UserType
from authentication.serializers import UserSerializer, UserTypeSerializer
from .models import *


# ============================================
# 	Payment, Items & Sales
# ============================================

# TODO degager pour mettre dans un module à part
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
		fields = '__all__'		# DEBUG
		# fields = ('id', 'name', 'api_url', 'sales')

	class JSONAPIMeta:
		pass
		# included_resources = ['sales']

class ItemGroupSerializer(serializers.ModelSerializer):
	# sale = ResourceRelatedField(
	# 	queryset = Sale.objects,
	# 	many = False
	# )
	items = ResourceRelatedField(
		queryset = Item.objects,
		many = True,
		related_link_view_name = 'item-list',
		related_link_url_kwarg = 'itemgroup_pk',
		self_link_view_name = 'itemgroup-relationships'
	)

	class Meta:
		model = ItemGroup
		fields = '__all__' 		# DEBUG

class ItemSerializer(serializers.ModelSerializer):
	"""
	Defines how the Item fields are serialized
	"""
	sale = ResourceRelatedField(
		queryset = Sale.objects,
		many = False
	)
	group = ResourceRelatedField(
		queryset = ItemGroup.objects,
		many = False
	)
	usertype = ResourceRelatedField(
		queryset = UserType.objects,
		many = False
	)

	included_serializers = {
		'sale': 'sales.serializers.SaleSerializer',
		'itemgroup': ItemGroupSerializer,
		'usertype': UserTypeSerializer
	}

	class Meta:
		model = Item
		fields = '__all__'		# DEBUG
		# fields = ('id', 'name', 'description', 'remaining_quantity',
				  # 'initial_quantity','sale_id', 'itemspecifications')

	class JSONAPIMeta:
		included_resources = ['itemgroup', 'sale', 'usertype']
		pass


class SaleSerializer(serializers.ModelSerializer):
	"""
	Defines how the Sale fields are serialized, without the payment methods
	"""
	# association = serializers.ReadOnlyField(source='association.name')
	association = ResourceRelatedField(
		queryset = Association.objects,
		many = False
	)
	items = ResourceRelatedField(
		queryset = Item.objects,
		many = True,
		related_link_view_name = 'item-list',
		related_link_url_kwarg = 'sale_pk',
		self_link_view_name = 'sale-relationships'
	)
	# orders = ResourceRelatedField(
	# 	queryset = Order.objects,
	# 	many = True
	# )

	included_serializers = {
		'association': 'sales.serializers.AssociationSerializer',
		'orders': 'sales.serializers.OrderSerializer',
		'items': ItemSerializer
	}

	class Meta:
		model = Sale
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'name', 'description', 'created_at', 'begin_at', 'end_at', 'max_payment_date', 'max_item_quantity', 'association', 'orders', 'items')

	class JSONAPIMeta:
		included_resources = ['items', 'association', 'orders']


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
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'name', 'bank_account', 'sales', 'foundation_id')

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
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'association', 'role', 'rights')

	class JSONAPIMeta:
		included_resources = ['association', 'user']


# ============================================
# 	Orders
# ============================================

class OrderSerializer(serializers.ModelSerializer):
	"""
	Defines how the Order fields are serialized
	"""
	user = ResourceRelatedField(
		queryset = User.objects,
		many = False
	)
	sale = ResourceRelatedField(
		queryset = Sale.objects,
		many = False
	)
	orderlines = ResourceRelatedField(
		queryset = OrderLine.objects,
		many = True,
		related_link_view_name='orderline-list',
		related_link_url_kwarg='order_pk',
		self_link_view_name='order-relationships'
	)

	included_serializers = {
		'user': UserSerializer,
		'sale': SaleSerializer,
		'orderlines': 'sales.serializers.OrderLineSerializer',
	}

	class Meta:
		model = Order
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'date','price', 'orderlines')

	class JSONAPIMeta:
		included_resources = ['orderlines', 'user', 'sale']

class OrderLineSerializer(serializers.ModelSerializer):
	"""
	Defines how the OrderLine fields are serialized
	"""
	# order = serializers.ReadOnlyField(source='order.id')
	order = ResourceRelatedField(
		queryset = Order.objects,
		many = False
	)	
	item = ResourceRelatedField(
		queryset = Item.objects,
		many = False,
		related_link_view_name='orderlineitem-list',
		related_link_url_kwarg='orderline_pk',
		self_link_view_name='orderline-relationships'
	)
	fields = ResourceRelatedField(
		queryset = OrderLineField.objects,
		many = True
	)

	included_serializers = {
		'item': ItemSerializer,
		'order': OrderSerializer,
		'fields': 'sales.serializers.OrderLineFieldSerializer'
	}

	class Meta:
		model = OrderLine
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'order', 'item', 'quantity')

	class JSONAPIMeta:
		included_resources = ['item', 'fields', 'order']


# ============================================
# 	Fields
# ============================================

class FieldSerializer(serializers.ModelSerializer):
	editable = serializers.BooleanField(source='itemfields.editable')

	class Meta:
		model = Field
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = []

class ItemFieldSerializer(serializers.ModelSerializer):
	item = ResourceRelatedField(
		queryset = Item.objects,
		many = False
	)
	field = ResourceRelatedField(
		queryset = Field.objects,
		many = False
	)

	included_serializers = {
		'item': ItemSerializer,
		'field': FieldSerializer,
	}

	class Meta:
		model = ItemField
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = ['field', 'item']

class OrderLineFieldSerializer(serializers.ModelSerializer):
	orderline = ResourceRelatedField(
		queryset = OrderLine.objects,
		many = False
	)
	field = ResourceRelatedField(
		queryset = Field.objects,
		many = False
	)

	included_serializers = {
		'orderline': OrderLineSerializer,
		'field': FieldSerializer,
	}

	class Meta:
		model = OrderLineField
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = ['orderline', 'field']

