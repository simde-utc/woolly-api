from rest_framework_json_api import serializers
from core.helpers import get_ResourceRelatedField

from authentication.models import User, UserType
from sales.models import AssociationMember, Order

class UserTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserType
		fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):

	usertype = get_ResourceRelatedField('users', 'usertypes', read_only=True, required=False)
	associations = get_ResourceRelatedField('users', 'associations', queryset=AssociationMember.objects, required=False)
	orders = get_ResourceRelatedField('users', 'orders', queryset=Order.objects, many=True, required=False)

	class Meta:
		model = User
		exclude = ('password',)

	included_serializers = {
		'usertype': UserTypeSerializer,
		'orders': 'sales.serializers.OrderSerializer'
		# 'associationmembers': AssociationMemberSerializer
	}

	class JSONAPIMeta:
		# included_resources = ['usertype', 'associationmembers']
		# included_resources = ['usertype']
		pass
