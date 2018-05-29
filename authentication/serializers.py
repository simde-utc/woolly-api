from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField

from authentication.models import User, UserType
from sales.models import Order

class UserTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserType
		fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):

	# password = serializers.CharField(required = True, write_only = True)
	type = serializers.ReadOnlyField(source='usertype.name')
	usertype = ResourceRelatedField(
		queryset = UserType.objects,
		related_link_view_name = 'usertype-list',
		related_link_url_kwarg = 'user_pk',
		self_link_view_name = 'user-relationships',
		required = False
	)
	"""
	associations = ResourceRelatedField(
		queryset=AssociationMember.objects,
		related_link_view_name='associationmember-list',
		related_link_url_kwarg='user_pk',
		self_link_view_name='user-relationships'
	)
	"""
	orders = ResourceRelatedField(
		queryset = Order.objects,
		many = True,
		# related_link_view_name = 'orders-list',
		# related_link_url_kwarg = 'user_pk',
		# self_link_view_name = 'user-relationships',
		required = False
	)


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
