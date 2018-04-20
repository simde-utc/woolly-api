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
		# fields = ('id', 'login', 'email', 'first_name', 'last_name', 'last_login', 'is_active', 'is_admin', 'woollyusertype', 'associationmembers')
		# write_only_fields = ('password',)

	def create(self, validated_data):
		# Login = None par défaut
		if 'login' not in validated_data or not validated_data['login']:
			validated_data['login'] = None
		# Sinon on vérifie l'unicité
		# else:
		# try:
		user = WoollyUser.objects.create(**validated_data) 
		# except IntegrityError as e:
		# 	print("EROOOOOOOOOOOOOOORORROOROROROROR")
		# 	if 'login' not in e or 'null' not in e:
		# 		raise IntegrityError(e)
			
		return user


	included_serializers = {
		'woollyusertype': WoollyUserTypeSerializer,
		# 'associationmembers': AssociationMemberSerializer
	}


	class JSONAPIMeta:
		# included_resources = ['woollyusertype', 'associationmembers']
		included_resources = ['woollyusertype']
