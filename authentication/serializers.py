from authentication.models import WoollyUser, WoollyUserType
# from sales.models import AssociationMember
# from sales.serializers import AssociationMemberSerializer
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from django.db import IntegrityError


class WoollyUserTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = WoollyUserType
		fields = ('id', 'name')


class WoollyUserSerializer(serializers.ModelSerializer):

	# password = serializers.CharField(required = True, write_only = True)
	"""
	woollyusertype = ResourceRelatedField(
		queryset = WoollyUserType.objects,
		related_link_view_name = 'user-type-list',
		related_link_url_kwarg = 'user_pk',
		self_link_view_name = 'user-relationships',
		required = False
	)
	associationmembers = ResourceRelatedField(
		queryset=AssociationMember.objects,
		related_link_view_name='associationmember-list',
		related_link_url_kwarg='user_pk',
		self_link_view_name='user-relationships'
	)
	"""

	class Meta:
		model = WoollyUser
		exclude = ('password',)

	def create(self, validated_data):
		"""
		Overload : set login to None if not a CAS user
		"""
		if 'login' not in validated_data or not validated_data['login']:
			validated_data['login'] = None
		return WoollyUser.objects.create(**validated_data) 


	included_serializers = {
		'woollyusertype': WoollyUserTypeSerializer,
		# 'associationmembers': AssociationMemberSerializer
	}


	class JSONAPIMeta:
		# included_resources = ['woollyusertype', 'associationmembers']
		included_resources = ['woollyusertype']
