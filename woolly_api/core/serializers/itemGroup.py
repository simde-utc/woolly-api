from rest_framework import serializers
from core.models import ItemGroup


class ItemGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemGroup
        fields = ('id', 'name')
