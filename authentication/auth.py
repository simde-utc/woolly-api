from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions

from .services import JWTClient, get_jwt_from_request

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
		claims = jwtClient.get_claims(jwt)
		try:
			user_id = claims['data']['user_id']
		except KeyError:
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
