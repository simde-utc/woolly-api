from rest_framework import serializers
from core.models.orderLine import OrderLine
from core.serializers.item import ItemSerializer


class OrderLineSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False, read_only= True)
    # Allow the API to send the items hyperlink
    #items = serializers.HyperlinkedRelatedField(many=True, view_name='item-detail', read_only=True)
    #order = serializers.ReadOnlyField(source='order.id')

    class Meta:
        model = OrderLine
        fields = ('id', 'item', 'quantity')
        read_only_fields = ('price',)
