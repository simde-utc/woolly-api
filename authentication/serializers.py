from authentication.models import User, UserType
# from sales.models import AssociationMember
# from sales.serializers import AssociationMemberSerializer
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from django.db import IntegrityError


class UserTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserType
		fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):

	# password = serializers.CharField(required = True, write_only = True)
	usertype = ResourceRelatedField(
		queryset = UserType.objects,
		related_link_view_name = 'user-type-list',
		related_link_url_kwarg = 'user_pk',
		self_link_view_name = 'user-relationships',
		required = False
	)
	"""
	associationmembers = ResourceRelatedField(
		queryset=AssociationMember.objects,
		related_link_view_name='associationmember-list',
		related_link_url_kwarg='user_pk',
		self_link_view_name='user-relationships'
	)
	"""

	class Meta:
		model = User
		exclude = ('password',)

	included_serializers = {
		'usertype': UserTypeSerializer,
		# 'associationmembers': AssociationMemberSerializer
	}

	class JSONAPIMeta:
		# included_resources = ['usertype', 'associationmembers']
		included_resources = ['usertype']
