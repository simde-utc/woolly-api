from rest_framework import serializers
from core.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Item
        fields = ('id', 'name', 'description', 'remaining_quantity', 'initial_quantity')