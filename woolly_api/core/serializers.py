from rest_framework import serializers
from .models import WoollyUser, Item, Order, OrderLine


class WoollyUserSerializer(serializers.Serializer):

    login = serializers.CharField(read_only=True, allow_blank=False, max_length=100)

    is_active = serializers.BooleanField(required=False)
    is_admin = serializers.BooleanField(required=False)

    def create(self, validated_data):
        """
        Create and return a new `WoollyUser` instance, given the validated data.
        """
        return WoollyUser.objects.create(**validated_data)
"""
    def update(self, instance, validated_data):

        Update and return an existing `WoollyUser` instance, given the validated data.

        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
"""

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Item
        fields = ('id', 'name', 'description', 'remaining_quantity', 'initial_quantity')

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
