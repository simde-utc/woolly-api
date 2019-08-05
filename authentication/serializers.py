from core.serializers import ModelSerializer
from rest_framework import serializers

from authentication.models import User, UserType
from sales.models import AssociationMember, Order

RelatedField = serializers.PrimaryKeyRelatedField


class UserTypeSerializer(ModelSerializer):
	class Meta:
		model = UserType
		fields = ('id', 'name')


class UserSerializer(ModelSerializer):

	usertype     = RelatedField(read_only=True, required=False)
	associations = RelatedField(queryset=AssociationMember.objects, many=True, required=False)
	orders       = RelatedField(queryset=Order.objects, many=True, required=False)

	included_serializers = {
		'usertype': UserTypeSerializer,
		'orders': 'sales.serializers.OrderSerializer',
		'associations': 'sales.serializers.AssociationSerializer',
	}

	class Meta:
		model = User
		exclude = ('password',)

