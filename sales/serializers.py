from .models import Sale, Item, ItemSpecifications, Association, Order
from .models import OrderLine, PaymentMethod, AssociationMember
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from authentication.models import UserType
from authentication.serializers import UserTypeSerializer


class ItemSpecificationsSerializer(serializers.ModelSerializer):
    """
        Defines how the ItemSpecifications fields are serialized
    """
    # Serializes a ForeignKey following JSON API convention
    usertype = ResourceRelatedField(
        queryset=UserType.objects,
        related_link_view_name='usertype-list',
        related_link_url_kwarg='itemspec_pk',
        self_link_view_name='itemSpecification-relationships'
    )

    # Required by JSON API
    included_serializers = {
        'usertype': UserTypeSerializer,
    }

    class Meta:
        """
            Precises which model and which fields to serialize
        """
        model = ItemSpecifications
        fields = ('id', 'usertype', 'price', 'quantity', 'nemopay_id','fun_id')

    class JSONAPIMeta:
        """
            Required by JSON API if you want to include the ForeignKey fields into the JSON
        """
        included_resources = ['usertype']


class ItemSerializer(serializers.ModelSerializer):
    """
        Defines how the Item fields are serialized
    """
    
    itemspecifications = ResourceRelatedField(
        queryset=ItemSpecifications.objects,
        many=True,
        related_link_view_name='itemSpecification-list',
        related_link_url_kwarg='item_pk',
        self_link_view_name='item-relationships'
    )

    included_serializers = {
        'itemspecifications': ItemSpecificationsSerializer,
    }

    class Meta:
        model = Item
        fields = ('id', 'name', 'description', 'remaining_quantity',
                  'initial_quantity','sale_id', 'itemspecifications')

    class JSONAPIMeta:
        included_resources = ['itemspecifications']


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


class SaleSerializer(serializers.ModelSerializer):
    """
        Defines how the Sale fields are serialized, without the payment methods
    """
    association = serializers.ReadOnlyField(source='association.name')
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
                  'end_date', 'max_payment_date', 'max_item_quantity', 'association',
                  'items')

    class JSONAPIMeta:
        included_resources = ['items']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
        Defines how the PaymentMethod fields are serialized
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

    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'api_url', 'sales')

    class JSONAPIMeta:
        included_resources = ['sales']


class SaleSerializer(serializers.ModelSerializer):
    """
        Defines how the Sale fields are serialized
    """
    association = serializers.ReadOnlyField(source='association.name')
    items = ResourceRelatedField(
        queryset=Item.objects,
        many=True,
        related_link_view_name='item-list',
        related_link_url_kwarg='sale_pk',
        self_link_view_name='sale-relationships'
    )

    included_serializers = {
        'items': ItemSerializer,
        'paymentmethods': PaymentMethodSerializer
    }

    class Meta:
        model = Sale
        fields = ('id', 'name', 'description', 'creation_date', 'begin_date',
                  'end_date', 'max_payment_date', 'max_item_quantity', 'association',
                  'items', 'paymentmethods')

    class JSONAPIMeta:
        included_resources = ['items', 'paymentmethods']


class AssociationSerializer(serializers.ModelSerializer):
    """
        Defines how the Association fields are serialized
    """
    sales = ResourceRelatedField(
        queryset=Sale.objects,
        many=True,
        related_link_view_name='sale-list',
        related_link_url_kwarg='association_pk',
        self_link_view_name='association-relationships'
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
        queryset=Association.objects,
        related_link_view_name='association-list',
        related_link_url_kwarg='associationmember_pk',
        self_link_view_name='associationmember-relationships'
    )

    included_serializers = {
        'association': AssociationSerializer,
    }

    class Meta:
        model = AssociationMember
        fields = ('id', 'association', 'role', 'rights')

    class JSONAPIMeta:
        included_resources = ['association']
