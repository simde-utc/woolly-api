from rest_framework_json_api import serializers
from core.helpers import get_ResourceRelatedField

from authentication.models import User, UserType
from authentication.serializers import UserSerializer, UserTypeSerializer
from .models import *


# ============================================
# 	Items & Sales
# ============================================

class ItemGroupSerializer(serializers.ModelSerializer):
	items = get_ResourceRelatedField('itemgroups', 'items', queryset=Item.objects, many=True, required=False)

	class Meta:
		model = ItemGroup
		fields = '__all__' 		# DEBUG

class ItemSerializer(serializers.ModelSerializer):
	sale     = get_ResourceRelatedField('items', 'sales', queryset=Sale.objects)
	group    = get_ResourceRelatedField('items', 'itemgroups', queryset=ItemGroup.objects)
	usertype = get_ResourceRelatedField('items', 'usertypes', queryset=UserType.objects)
	fields   = get_ResourceRelatedField('items', 'fields', queryset=Field.objects, many=True, required=False)
	
	quantity_left = serializers.IntegerField(read_only=True)

	included_serializers = {
		'itemfields': 'sales.serializers.ItemFieldSerializer',
		'sale': 'sales.serializers.SaleSerializer',
		'itemgroup': ItemGroupSerializer,
		'usertype': UserTypeSerializer,
	}

	class Meta:
		model = Item
		fields = '__all__'		# DEBUG
		# fields = ('id', 'name', 'description', 'remaining_quantity',
				  # 'initial_quantity','sale_id', 'itemspecifications')

	class JSONAPIMeta:
		# included_resources = ['itemgroup', 'sale', 'usertype']
		pass


class SaleSerializer(serializers.ModelSerializer):
	association = get_ResourceRelatedField('sales', 'associations', queryset=Association.objects, required=True)
	orders      = get_ResourceRelatedField('sales', 'orders', queryset=Order.objects, many=True, required=False)
	items       = get_ResourceRelatedField('sales', 'items', queryset=Item.objects, many=True, required=False)

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
		# included_resources = ['items', 'association', 'orders']		# TODO Inutiles par défault ??
		pass


# ============================================
# 	Associations
# ============================================

class AssociationSerializer(serializers.ModelSerializer):
	sales = get_ResourceRelatedField('associations', 'sales', queryset=Sale.objects, many=True, required=False)
	# members

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
	association = get_ResourceRelatedField('associationmembers', 'associations', queryset=Association.objects)
	user        = get_ResourceRelatedField('associationmembers', 'users', queryset=User.objects)

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
	owner = get_ResourceRelatedField('orders', 'users', queryset=User.objects, required=False)
	sale  = get_ResourceRelatedField('orders', 'sales', queryset=Sale.objects)
	orderlines = get_ResourceRelatedField(
		'orders', 'orderlines', queryset=OrderLine.objects,
		many=True, required=False, allow_null=True
	)

	included_serializers = {
		'owner': UserSerializer,
		'sale': SaleSerializer,
		'orderlines': 'sales.serializers.OrderLineSerializer',
	}

	class Meta:
		model = Order
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'date','price', 'orderlines')

	class JSONAPIMeta:
		# included_resources = ['orderlines', 'owner', 'sale']
		pass

class OrderLineSerializer(serializers.ModelSerializer):
	# order = serializers.ReadOnlyField(source='order.id')
	order = get_ResourceRelatedField('orderlines', 'orders', queryset=Order.objects)
	item  = get_ResourceRelatedField('orderlines', 'items', queryset=Item.objects)
	orderlineitems = get_ResourceRelatedField(
		'orderlines', 'orderlineitems', queryset=OrderLineItem.objects,
		many=True, required=False, allow_null=True
	)

	included_serializers = {
		'item': ItemSerializer,
		'order': OrderSerializer,
		'orderlineitems': 'sales.serializers.OrderLineItemSerializer'
	}

	class Meta:
		model = OrderLine
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'order', 'item', 'quantity')

	class JSONAPIMeta:
		# included_resources = ['item', 'order', 'fields']
		pass


# ============================================
# 	Fields
# ============================================

class FieldSerializer(serializers.ModelSerializer):
	itemfields = get_ResourceRelatedField('fields', 'itemfields', queryset='ItemField.objects', many=True, required=False)

	included_serializers = {
		'itemfields': 'sales.serializers.ItemFieldSerializer',
	}

	class Meta:
		model = Field
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = []

class ItemFieldSerializer(serializers.ModelSerializer):
	item  = get_ResourceRelatedField('itemfields', 'items', queryset=Item.objects)
	field = get_ResourceRelatedField('itemfields', 'fields', queryset=Field.objects)

	included_serializers = {
		'item': ItemSerializer,
		'field': FieldSerializer,
	}

	class Meta:
		model = ItemField
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = ['field', 'item']


class OrderLineItemSerializer(serializers.ModelSerializer):
	orderline       = get_ResourceRelatedField('orderlineitems', 'orderlines', queryset=OrderLine.objects)
	orderlinefields = get_ResourceRelatedField(
		'orderlineitems', 'orderlinefields', queryset=OrderLineField.objects,
		many=True, required=False, allow_null=True
	)

	included_serializers = {
		'orderline': OrderLineSerializer,
		'orderlinefields': 'sales.serializers.OrderLineFieldSerializer'
	}

	class Meta:
		model = OrderLineItem
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		# included_resources = ['orderlinefields']
		pass

class OrderLineFieldSerializer(serializers.ModelSerializer):
	orderlineitem = get_ResourceRelatedField('orderlinefields', 'orderlineitems', queryset=OrderLineItem.objects)
	field         = get_ResourceRelatedField('orderlinefields', 'fields', queryset=Field.objects)

	# For easier access
	name 	 = serializers.CharField(read_only=True, source='field.name')
	type 	 = serializers.CharField(read_only=True, source='field.type')
	editable = serializers.BooleanField(read_only=True, source='isEditable')

	included_serializers = {
		'orderlineitem': OrderLineItemSerializer,
		'field': FieldSerializer,
	}

	class Meta:
		model = OrderLineField
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = ['orderlineitem', 'field']

