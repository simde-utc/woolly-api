from .models import Sale, Item, ItemSpecifications, Association, WoollyUserType
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField


class WoollyUserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = WoollyUserType
        fields = ('id', 'name')


class ItemSpecificationsSerializer(serializers.ModelSerializer):
    # Pour une raison inconnue, la view plante quand on rajoute les champs
    # price et quantity en disant qu'il n'existe pas dans la classe WoollyUserType
    # usertype = serializers.CharField(source='woolly_user_type.name') -> fait
    # egalement planter la view
    # usertype = WoollyUserTypeSerializer(many=False, read_only=True)
    woolly_user_type = ResourceRelatedField(
        queryset=WoollyUserType.objects,
        related_link_view_name='usertype-list',
        related_link_url_kwarg='itemspec_pk',
        self_link_view_name='itemSpecification-relationships'
    )

    class Meta:
        model = ItemSpecifications
        fields = ('id', 'woolly_user_type')


class ItemSpecificationsSerializer2(serializers.ModelSerializer):
    # Faite pour essayer de regler le probleme du dessus
    # usertype = WoollyUserTypeSerializer(many=False, read_only=True)
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
        fields = ('id', 'woolly_user_type', 'price', 'quantity')

    class JSONAPIMeta:
        included_resources = ['woolly_user_type']


class ItemSerializer(serializers.ModelSerializer):
    # itemGroup = ItemGroupSerializer(required=False, read_only=True)
    # specifications = ItemSpecificationsSerializer(many=True, read_only=True)
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


class SaleSerializer(serializers.ModelSerializer):
    # items = ItemSerializer(many=True, read_only=True)
    asso = serializers.ReadOnlyField(source='association.name')
    items = ResourceRelatedField(
        queryset=Item.objects,
        many=True,
        related_link_view_name='item-list',
        related_link_url_kwarg='sale_pk',
        self_link_view_name='sale-relationships'
    )

    included_serializers = {
        'items': ItemSerializer,
    }

    class Meta:
        model = Sale
        fields = ('id', 'name', 'description', 'creation_date', 'begin_date',
                  'end_date', 'max_payment_date', 'max_item_quantity', 'asso',
                  'items')

    class JSONAPIMeta:
        included_resources = ['items']


class AssociationSerializer(serializers.ModelSerializer):
    # sales = SaleSerializer(many=True, read_only=True)
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
        fields = ('id', 'name', 'bank_account', 'sales')

    class JSONAPIMeta:
        included_resources = ['sales']
