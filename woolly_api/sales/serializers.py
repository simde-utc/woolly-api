from .models import Sale, Item, ItemSpecifications, Association, Order
from .models import OrderLine, PaymentMethod
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from authentication.models import WoollyUserType
from authentication.serializers import WoollyUserTypeSerializer


class ItemSpecificationsSerializer(serializers.ModelSerializer):
    woolly_user_type = ResourceRelatedField(
        queryset=WoollyUserType.objects,
        related_link_view_name='usertype-list',
        related_link_url_kwarg='itemspec_pk',
        self_link_view_name='itemSpecification-relationships'
    )

    included_serializers = {
        'woolly_user_type': WoollyUserTypeSerializer,
    }

    class Meta:
        model = ItemSpecifications
        fields = ('id', 'woolly_user_type', 'price', 'quantity', 'nemopay_id')

    class JSONAPIMeta:
        included_resources = ['woolly_user_type']


class ItemSerializer(serializers.ModelSerializer):
    specifications = ResourceRelatedField(
        queryset=ItemSpecifications.objects,
        many=True,
        related_link_view_name='itemSpecification-list',
        related_link_url_kwarg='item_pk',
        self_link_view_name='item-relationships'
    )

    included_serializers = {
        'specifications': ItemSpecificationsSerializer,
    }

    class Meta:
        model = Item
        fields = ('id', 'name', 'description', 'remaining_quantity',
                  'initial_quantity', 'specifications')

    class JSONAPIMeta:
        included_resources = ['specifications']


class OrderLineSerializer(serializers.ModelSerializer):
    order = serializers.ReadOnlyField(source='order.id')

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
    items = ResourceRelatedField(
        queryset=OrderLine.objects,
        many=True,
        related_link_view_name='orderline-list',
        related_link_url_kwarg='order_pk',
        self_link_view_name='order-relationships'
    )

    included_serializers = {
        'items': OrderLineSerializer,
    }

    class Meta:
        model = Order
        fields = ('id', 'status', 'date', 'items')

    class JSONAPIMeta:
        included_resources = ['items']


class SalePSerializer(serializers.ModelSerializer):
    asso = serializers.ReadOnlyField(source='association.name')
    items = ResourceRelatedField(
        queryset=Item.objects,
        many=True,
        related_link_view_name='item-list',
        related_link_url_kwarg='sale_pk',
        self_link_view_name='sale-relationships'
    )

    included_serializers = {
        'items': ItemSerializer
    }

    class Meta:
        model = Sale
        fields = ('id', 'name', 'description', 'creation_date', 'begin_date',
                  'end_date', 'max_payment_date', 'max_item_quantity', 'asso',
                  'items')

    class JSONAPIMeta:
        included_resources = ['items']


class PaymentMethodSerializer(serializers.ModelSerializer):

    sales = ResourceRelatedField(
        queryset=Sale.objects,
        many=True,
        related_link_view_name='sale-payment-list',
        related_link_url_kwarg='payment_pk',
        self_link_view_name='paymentmethod-relationships'
    )

    included_serializers = {
        'sales': SalePSerializer
    }

    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'api_url', 'sales')

    class JSONAPIMeta:
        included_resources = ['sales']


class SaleSerializer(serializers.ModelSerializer):
    asso = serializers.ReadOnlyField(source='association.name')
    items = ResourceRelatedField(
        queryset=Item.objects,
        many=True,
        related_link_view_name='item-list',
        related_link_url_kwarg='sale_pk',
        self_link_view_name='sale-relationships'
    )
    """
    payment_methods = ResourceRelatedField(
        queryset=PaymentMethod.objects,
        many=True,
        related_link_view_name='paymentmethod-list',
        related_link_url_kwarg='sale_pk',
        self_link_view_name='sale-relationships'
    )
    """
    included_serializers = {
        'items': ItemSerializer,
        'payment_methods': PaymentMethodSerializer
    }

    class Meta:
        model = Sale
        fields = ('id', 'name', 'description', 'creation_date', 'begin_date',
                  'end_date', 'max_payment_date', 'max_item_quantity', 'asso',
                  'items', 'payment_methods')

    class JSONAPIMeta:
        included_resources = ['items', 'payment_methods']


class AssociationSerializer(serializers.ModelSerializer):
    sales = ResourceRelatedField(
        queryset=Sale.objects,
        many=True,
        related_link_view_name='sale-list',
        related_link_url_kwarg='association_pk',
        self_link_view_name='association-relationships'
    )

    included_serializers = {
        'sales': SaleSerializer,
    }

    class Meta:
        model = Association
        fields = ('id', 'name', 'bank_account', 'sales', 'foundation_id')

    class JSONAPIMeta:
        included_resources = ['sales']
