from rest_framework import serializers
from core.models import Item, ItemGroup
from core.serializers.itemGroup import ItemGroupSerializer


class ItemSerializer(serializers.ModelSerializer):
    itemGroup = serializers.CharField(source='item_group.name')
    #itemGroup = ItemGroupSerializer(many=False, read_only= True)
    #itemGroup = serializers.HyperlinkedRelatedField(many=True, view_name='itemGroup-detail', read_only=True)
    class Meta:
        model = Item
        fields = ('id', 'name', 'description', 'remaining_quantity', 'initial_quantity', 'itemGroup')
