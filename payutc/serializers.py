from authentication.models import User, UserType
# from sales.models import AssociationMember
# from sales.serializers import AssociationMemberSerializer
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ('id', 'name')


class UserSerializer(serializers.Serializer):
    login = serializers.CharField(
        allow_blank=False, max_length=253, required=True)
    password = serializers.CharField(required=True)

    usertype = ResourceRelatedField(
        queryset=UserType.objects,
        related_link_view_name='user-type-list',
        related_link_url_kwarg='user_pk',
        self_link_view_name='user-relationships'
    )
    """
    associationmembers = ResourceRelatedField(
        queryset=AssociationMember.objects,
        related_link_view_name='associationmember-list',
        related_link_url_kwarg='user_pk',
        self_link_view_name='user-relationships'
    )
    """
    included_serializers = {
        'usertype': UserTypeSerializer,
        # 'associationmembers': AssociationMemberSerializer
    }

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = User
        fields = ('id', 'login', 'last_login', 'type_id',  'password', 'is_active',
                  'is_admin', 'usertype', 'associationmembers')
        write_only_fields = ('password',)

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        return User.objects.create(**validated_data)

    class JSONAPIMeta:
        included_resources = ['usertype', 'associationmembers']
