from rest_framework import serializers
from core.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #items = ItemSerializer(many=True, queryset=Item.objects.all())
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