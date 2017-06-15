from authentication.models import WoollyUser, WoollyUserType
from sales.models import AssociationMember
#from sales.serializers import AssociationMemberSerializer
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField


class WoollyUserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoollyUserType
        fields = ('id', 'name')


class WoollyUserSerializer(serializers.Serializer):
    login = serializers.CharField(allow_blank=False, max_length=253, required=True)
    password = serializers.CharField(required=True)
    woollyusertype = ResourceRelatedField(
        queryset=WoollyUserType.objects,
        related_link_view_name='user-type-list',
        related_link_url_kwarg='user_pk',
        self_link_view_name='user-relationships'
    )
    """
    associations = ResourceRelatedField(
        queryset=AssociationMember.objects,
        related_link_view_name='associationmember-list',
        related_link_url_kwarg='user_pk',
        self_link_view_name='user-relationships'
    )
    """
    included_serializers = {
        'woollyusertype': WoollyUserTypeSerializer,
        # 'associations': AssociationMemberSerializer,
    }

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = WoollyUser
        fields = ('id', 'login', 'last_login', 'type_id',  'password', 'is_active', 'is_admin', 'woollyusertype')
        write_only_fields = ('password',)

    def create(self, validated_data):
        """
        Create and return a new `WoollyUser` instance, given the validated data.
        """
        return WoollyUser.objects.create(**validated_data)

    class JSONAPIMeta:
        included_resources = ['type']
