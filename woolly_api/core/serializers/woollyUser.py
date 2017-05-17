from rest_framework import serializers
from core.models import WoollyUser


class WoollyUserSerializer(serializers.Serializer):

    login = serializers.CharField(read_only=True, allow_blank=False, max_length=100)

    is_active = serializers.BooleanField(required=False)
    is_admin = serializers.BooleanField(required=False)

    def create(self, validated_data):
        """
        Create and return a new `WoollyUser` instance, given the validated data.
        """
        return WoollyUser.objects.create(**validated_data)