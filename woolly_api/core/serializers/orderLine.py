from core.models.orderLine import OrderLine
from core.serializers.item import ItemSerializer
from rest_framework import serializers
from core.models.order import Order
from core.models.item import Item
from core.models.orderLine import OrderLine
from core.serializers.item import ItemSerializer

class OrderSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only= True)
    # Allow the API to send the items hyperlink
    #items = serializers.HyperlinkedRelatedField(many=True, view_name='item-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.login')
    #lines = OrderLineSerializer(many=True, read_only=True)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Order
        fields = ('id', 'quantity', 'user', 'items', 'date')
        read_only_fields = ('date',)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item in items_data:
            d=dict(item)
            Item.objects.create(order=order, name=d['name'])
        return order

class OrderLineSerializer(serializers.HyperlinkedModelSerializer):
    item = ItemSerializer(many=False, read_only=True)
    #order = OrderSerializer(many=False, read_only= True)
    # Allow the API to send the items hyperlink
    #items = serializers.HyperlinkedRelatedField(many=False, view_name='cart-detail', read_only=True)
    # order = serializers.ReadOnlyField(source='order.id')

    class Meta:
        model = OrderLine
        fields = ('id', 'item', 'quantity')
