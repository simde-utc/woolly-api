from authentication.serializers import UserSerializer, UserTypeSerializer
from authentication.models import User, UserType
from core.serializers import ModelSerializer
from rest_framework import serializers
from .models import *

RelatedField = serializers.PrimaryKeyRelatedField


# ============================================
# 	Items & Sales
# ============================================

class ItemGroupSerializer(ModelSerializer):
	items = RelatedField(queryset=Item.objects, many=True, required=False)

	class Meta:
		model = ItemGroup
		fields = '__all__' 		# DEBUG

class ItemSerializer(ModelSerializer):
	sale     = RelatedField(queryset=Sale.objects)
	group    = RelatedField(queryset=ItemGroup.objects)
	usertype = RelatedField(queryset=UserType.objects)
	fields   = RelatedField(queryset=Field.objects, many=True, required=False)
	
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


class SaleSerializer(ModelSerializer):
	association = RelatedField(queryset=Association.objects, required=True)
	orders      = RelatedField(queryset=Order.objects, many=True, required=False)
	items       = RelatedField(queryset=Item.objects, many=True, required=False)

	included_serializers = {
		'association': 'sales.serializers.AssociationSerializer',
		'orders': 'sales.serializers.OrderSerializer',
		'items': ItemSerializer
	}

	class Meta:
		model = Sale
		fields = '__all__'


# ============================================
# 	Associations
# ============================================

class AssociationSerializer(ModelSerializer):
	sales = RelatedField(queryset=Sale.objects, many=True, required=False)
	# members

	included_serializers = {
		'sales': SaleSerializer
	}

	class Meta:
		model = Association
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'name', 'bank_account', 'sales', 'foundation_id')


# ============================================
# 	Orders
# ============================================

class OrderSerializer(ModelSerializer):
	owner = RelatedField(queryset=User.objects, required=False)
	sale  = RelatedField(queryset=Sale.objects)
	orderlines = RelatedField(queryset=OrderLine.objects,
														many=True, required=False, allow_null=True)

	included_serializers = {
		'owner': UserSerializer,
		'sale': SaleSerializer,
		'orderlines': 'sales.serializers.OrderLineSerializer',
	}

	class Meta:
		model = Order
		fields = '__all__' 		# DEBUG
		# fields = ('id', 'date','price', 'orderlines')

class OrderLineSerializer(ModelSerializer):
	# order = serializers.ReadOnlyField(source='order.id')
	order = RelatedField(queryset=Order.objects)
	item  = RelatedField(queryset=Item.objects)
	orderlineitems = RelatedField(queryset=OrderLineItem.objects,
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


# ============================================
# 	Fields
# ============================================

class FieldSerializer(ModelSerializer):
	itemfields = RelatedField(queryset='ItemField.objects', many=True, required=False)

	included_serializers = {
		'itemfields': 'sales.serializers.ItemFieldSerializer',
	}

	class Meta:
		model = Field
		fields = '__all__' 		# DEBUG

class ItemFieldSerializer(ModelSerializer):
	item  = RelatedField(queryset=Item.objects)
	field = RelatedField(queryset=Field.objects)

	included_serializers = {
		'item': ItemSerializer,
		'field': FieldSerializer,
	}

	class Meta:
		model = ItemField
		fields = '__all__' 		# DEBUG


class OrderLineItemSerializer(ModelSerializer):
	orderline       = RelatedField(queryset=OrderLine.objects)
	orderlinefields = RelatedField(queryset=OrderLineField.objects,
		many=True, required=False, allow_null=True
	)

	included_serializers = {
		'orderline': OrderLineSerializer,
		'orderlinefields': 'sales.serializers.OrderLineFieldSerializer'
	}

	class Meta:
		model = OrderLineItem
		fields = '__all__' 		# DEBUG

class OrderLineFieldSerializer(ModelSerializer):
	orderlineitem = RelatedField(queryset=OrderLineItem.objects)
	field         = RelatedField(queryset=Field.objects)

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
