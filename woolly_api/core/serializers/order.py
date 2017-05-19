from rest_framework import serializers
from core.models import Order, Item
from core.serializers import ItemSerializer


class OrderSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only= True)
    # Allow the API to send the items hyperlink
    #items = serializers.HyperlinkedRelatedField(many=True, view_name='item-detail', read_only=True)
    user = serializers.ReadOnlyField(source='user.login')

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
