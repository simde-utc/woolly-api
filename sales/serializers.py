from rest_framework_json_api import serializers
from core.helpers import get_ResourceRelatedField

from authentication.models import User, UserType
from authentication.serializers import UserSerializer, UserTypeSerializer
from .models import *


# ============================================
# 	Items & Sales
# ============================================

class ItemGroupSerializer(serializers.ModelSerializer):
	items = get_ResourceRelatedField('itemgroup', 'item', queryset=Item.objects, many=True, required=False)

	class Meta:
		model = ItemGroup
		fields = '__all__' 		# DEBUG

class ItemSerializer(serializers.ModelSerializer):
	sale     = get_ResourceRelatedField('item', 'sale', queryset=Sale.objects)
	group    = get_ResourceRelatedField('item', 'itemgroup', queryset=ItemGroup.objects)
	usertype = get_ResourceRelatedField('item', 'usertype', queryset=UserType.objects)
	fields   = get_ResourceRelatedField('item', 'field', queryset=Field.objects, many=True, required=False)
	
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


class SaleSerializer(serializers.HyperlinkedModelSerializer):
	association = get_ResourceRelatedField('sale', 'association', queryset=Association.objects, required=True)
	orders      = get_ResourceRelatedField('sale', 'order', queryset=Order.objects, many=True, required=False)
	items       = get_ResourceRelatedField('sale', 'item', queryset=Item.objects, many=True, required=False)

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
	sales = get_ResourceRelatedField('association', 'sale', queryset=Sale.objects, many=True, required=False)
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
	association = get_ResourceRelatedField('associationmember', 'association', queryset=Association.objects)
	user        = get_ResourceRelatedField('associationmember', 'user', queryset=User.objects)

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
	owner = get_ResourceRelatedField('order', 'user', queryset=User.objects, required=False)
	sale  = get_ResourceRelatedField('order', 'sale', queryset=Sale.objects)
	orderlines = get_ResourceRelatedField(
		'order', 'orderlines', queryset=OrderLine.objects,
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
	order = get_ResourceRelatedField('orderline', 'order', queryset=Order.objects)
	item  = get_ResourceRelatedField('orderline', 'item', queryset=Item.objects)
	orderlineitems = get_ResourceRelatedField(
		'orderline', 'orderlineitems', queryset=OrderLineItem.objects,
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
	itemfields = get_ResourceRelatedField('field', 'itemfield', queryset='ItemField.objects', many=True)

	included_serializers = {
		'itemfields': 'sales.serializers.ItemFieldSerializer',
	}

	class Meta:
		model = Field
		fields = '__all__' 		# DEBUG

	class JSONAPIMeta:
		included_resources = []

class ItemFieldSerializer(serializers.ModelSerializer):
	item  = get_ResourceRelatedField('itemfield', 'item', queryset=Item.objects)
	field = get_ResourceRelatedField('itemfield', 'field', queryset=Field.objects)

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
	orderline       = get_ResourceRelatedField('orderlineitem', 'orderline', queryset=OrderLine.objects)
	orderlinefields = get_ResourceRelatedField(
		'orderlineitem', 'orderlinefield', queryset=OrderLineField.objects,
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
	orderlineitem = get_ResourceRelatedField('orderlinefield', 'orderlineitem', queryset=OrderLineItem.objects)
	field         = get_ResourceRelatedField('orderlinefield', 'field', queryset=Field.objects)

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

