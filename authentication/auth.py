from django.contrib.auth import get_user_model
from django import forms
from rest_framework import authentication
from rest_framework import exceptions
from .services import JWTClient
from .helpers import get_jwt_from_request


class JWTAuthentication(authentication.BaseAuthentication):
	"""
	Authenticate User frow JWT
	"""
	def authenticate(self, request):
		"""
		Return the user from the JWT sent in the request
		"""
		# Get JWT from request header
		jwt = get_jwt_from_request(request)
		if jwt == None:
			return None

		# Get user id
		jwtClient = JWTClient()
		try:
			claims = jwtClient.get_claims(jwt)
			user_id = claims['data']['user_id']
		except:
			return None
		if user_id == None:
			return None

		# Try logging user
		UserModel = get_user_model()
		try:
			user = UserModel.objects.get(id=user_id)
		except UserModel.DoesNotExist:
			raise exceptions.AuthenticationFailed("User does not exist.")
		return (user, None)


class AdminSiteBackend:
	def authenticate(self, request, username = None, password = None):
		print(request)

		UserModel = get_user_model()
		# Try to fetch user
		try:
			user = UserModel.objects.get(**{ UserModel.USERNAME_FIELD: username })
		except UserModel.DoesNotExist:
			return None


		# Check password
		if password != "azd":
			return None

		return user

	def get_user(self, user_id):
		UserModel = get_user_model()
		try:
			user = UserModel.objects.get(id=user_id)
		except UserModel.DoesNotExist:
			return None
