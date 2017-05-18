from rest_framework import serializers
from core.models import WoollyUser, WoollyUserType


class WoollyUserSerializer(serializers.Serializer):

    login = serializers.CharField(allow_blank=False, max_length=253, required=True)
    password = serializers.CharField(required=True)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = WoollyUser
        fields = ('id', 'login', 'last_login', 'type_id',  'password', 'is_active', 'is_admin', )
        write_only_fields = ('password',)

    def create(self, validated_data):
        """
        Create and return a new `WoollyUser` instance, given the validated data.
        """
        return WoollyUser.objects.create(**validated_data)