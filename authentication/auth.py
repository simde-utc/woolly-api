import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext as _
from django.forms import ValidationError
from rest_framework import authentication
from rest_framework import exceptions

from woolly_api.settings import JWT_SECRET_KEY
from .helpers import get_jwt_from_request
from joserfc.jwt import decode as decode_jwt

UserModel = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
	"""
	Authenticate User frow JWT, used in the API
	"""
	def authenticate(self, request):
		"""
		Return the user from the JWT sent in the request
		"""
		# Get JWT from request header
		jwt = get_jwt_from_request(request)
		if jwt is None:
			return None

		try:
			claims = decode_jwt(jwt, JWT_SECRET_KEY).claims
			user_id = claims['data']['user_id']
		except:
			return None
		if user_id == None:
			return None

		# Try logging user
		try:
			return UserModel.objects.get(id=user_id) , None
		except UserModel.DoesNotExist:
			raise exceptions.AuthenticationFailed("User does not exist.")


class AdminSiteBackend(ModelBackend):
	"""
	Authenticate User from email - password, used in the admin site
	"""

	def authenticate(self, request, username=None, password=None, **kwargs):
		# Try to fetch user
		try:
			user = UserModel.objects.get(**{ UserModel.USERNAME_FIELD: username })
		except UserModel.DoesNotExist:
			return None

		# Check password
		if not user.check_password(password):
			return None

		# Check if admin
		if not user.is_admin:
			raise ValidationError(
				_("This account is not allowed."),
				code='not_allowed',
			)

		return user

	def get_user(self, user_id):
		try:
			return UserModel.objects.get(id=user_id)
		except UserModel.DoesNotExist:
			return None
