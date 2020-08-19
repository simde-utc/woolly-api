from rest_framework import serializers

from core.serializers import ModelSerializer, APIModelSerializer
from authentication.serializers import UserSerializer, UserTypeSerializer
from authentication.models import User, UserType

from sales.models import (
    Association, Sale, ItemGroup, Item, Order,
    OrderLine, OrderLineItem, Field, ItemField, OrderLineField
)

RelatedField = serializers.PrimaryKeyRelatedField


# --------------------------------------------
#   Items
# --------------------------------------------

class ItemGroupSerializer(ModelSerializer):
    sale  = RelatedField(queryset=Sale.objects.all())
    items = RelatedField(queryset=Item.objects.all(), many=True, required=False)

    included_serializers = {
        'sale': 'sales.serializers.SaleSerializer',
        'items': 'sales.serializers.ItemSerializer',
    }

    class Meta:
        model = ItemGroup
        fields = (
            "id", "name", "description", "max_per_user", "is_active",
            "sale", "items",
        )
        manager_fields = ("quantity", )


class ItemSerializer(ModelSerializer):
    sale       = RelatedField(queryset=Sale.objects.all())
    group      = RelatedField(queryset=ItemGroup.objects.all(), allow_null=True, required=False)
    usertype   = RelatedField(queryset=UserType.objects.all())
    itemfields = RelatedField(many=True, read_only=True)

    quantity_left = serializers.IntegerField(read_only=True)
    quantity_sold = serializers.IntegerField(read_only=True)

    included_serializers = {
        'itemfields': 'sales.serializers.ItemFieldSerializer',
        'sale': 'sales.serializers.SaleSerializer',
        'itemgroup': ItemGroupSerializer,
        'usertype': UserTypeSerializer,
    }

    class Meta:
        model = Item
        fields = (
            "id", "name", "description", "price", "max_per_user", "is_active",
            "fields", "itemfields", "sale", "group", "usertype",
        )
        manager_fields = ("quantity", "quantity_left", "quantity_sold")


# --------------------------------------------
#   Associations
# --------------------------------------------

class SaleSerializer(ModelSerializer):
    id          = serializers.SlugField(max_length=50, min_length=6, allow_blank=False)
    association = RelatedField(queryset=Association.objects.all(), required=True)
    orders      = RelatedField(queryset=Order.objects.all(), many=True, required=False)
    itemgroups  = RelatedField(queryset=ItemGroup.objects.all(), many=True, required=False)
    items       = RelatedField(queryset=Item.objects.all(), many=True, required=False)

    included_serializers = {
        'association': 'sales.serializers.AssociationSerializer',
        'orders': 'sales.serializers.OrderSerializer',
        'itemgroups': ItemGroupSerializer,
        'items': ItemSerializer,
    }

    class Meta:
        model = Sale
        fields = (
            "id", "name", "description", "association", "is_active",
            "cgv", "image", "color",
        )
        manager_fields = (
            "is_public", "begin_at", "end_at",
            "max_item_quantity", "orders",
        )


class AssociationSerializer(APIModelSerializer):
    sales = RelatedField(queryset=Sale.objects.all(), many=True, required=False)

    included_serializers = {
        'sales': SaleSerializer
    }

    class Meta:
        model = Association
        fields = ("id", "shortname", "fun_id")


# --------------------------------------------
#   Orders
# --------------------------------------------

class OrderSerializer(ModelSerializer):
    owner = RelatedField(queryset=User.objects.all(), required=False)
    sale  = RelatedField(queryset=Sale.objects.all())
    orderlines = RelatedField(queryset=OrderLine.objects.all(),
                              many=True, required=False, allow_null=True)

    included_serializers = {
        'owner': UserSerializer,
        'sale': SaleSerializer,
        'orderlines': 'sales.serializers.OrderLineSerializer',
    }

    class Meta:
        model = Order
        fields = ("id", "owner", "sale", "status", "updated_at", "orderlines")


class OrderLineSerializer(ModelSerializer):
    # order = serializers.ReadOnlyField(source='order.id')
    order = RelatedField(queryset=Order.objects.all())
    item  = RelatedField(queryset=Item.objects.all())
    orderlineitems = RelatedField(queryset=OrderLineItem.objects.all(),
                                  many=True, required=False, allow_null=True)

    included_serializers = {
        'item': ItemSerializer,
        'order': OrderSerializer,
        'orderlineitems': 'sales.serializers.OrderLineItemSerializer'
    }

    class Meta:
        model = OrderLine
        fields = "__all__"


class OrderLineItemSerializer(ModelSerializer):
    orderline       = RelatedField(queryset=OrderLine.objects.all())
    orderlinefields = RelatedField(queryset=OrderLineField.objects.all(),
                                   many=True, required=False, allow_null=True)

    included_serializers = {
        'orderline': OrderLineSerializer,
        'orderlinefields': 'sales.serializers.OrderLineFieldSerializer'
    }

    class Meta:
        model = OrderLineItem
        fields = "__all__"


# --------------------------------------------
#   Fields
# --------------------------------------------

class FieldSerializer(ModelSerializer):
    itemfields = RelatedField(queryset='ItemField.objects.all()', many=True, required=False)

    included_serializers = {
        'itemfields': 'sales.serializers.ItemFieldSerializer',
    }

    class Meta:
        model = Field
        fields = ("id", "type", "name", "default")


class ItemFieldSerializer(ModelSerializer):
    item  = RelatedField(queryset=Item.objects.all())
    field = RelatedField(queryset=Field.objects.all())

    included_serializers = {
        'item': ItemSerializer,
        'field': FieldSerializer,
    }

    class Meta:
        model = ItemField
        fields = "__all__"


class OrderLineFieldSerializer(ModelSerializer):
    orderlineitem = RelatedField(queryset=OrderLineItem.objects.all())
    field         = RelatedField(queryset=Field.objects.all())

    # For easier access
    name     = serializers.CharField(read_only=True, source='field.name')
    type     = serializers.CharField(read_only=True, source='field.type')
    editable = serializers.BooleanField(read_only=True, source='is_editable')

    included_serializers = {
        'orderlineitem': OrderLineItemSerializer,
        'field': FieldSerializer,
    }

    class Meta:
        model = OrderLineField
        fields = '__all__'      # DEBUG
