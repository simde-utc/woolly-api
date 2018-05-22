from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from .services import JWTClient
from .views import get_jwt_from_request

class JWTBackend:
	"""
	Backend to log user frow JWT
	"""
	def __init__(self):
		self.jwtClient = JWTClient()
		# One-time configuration and initialization.

	def authenticate(self, request):
		"""
		Return the user from the JWT sent in the request
		"""
		# Get JWT from request header
		jwt = get_jwt_from_request(request)
		if jwt == None:
			return AnonymousUser

		# Get user id
		claims = self.jwtClient.get_claims(jwt)
		try:
			user_id = claims['data']['user_id']
		except KeyError:
			return AnonymousUser
		if user_id == None:
			return AnonymousUser

		# Try logging user
		UserModel = get_user_model()
		try:
			return UserModel.objects.get(id=user_id)
		except UserModel.DoesNotExist:
			return AnonymousUser


# """
# Inutiles ?

from cas.backends import CASBackend
from cas.backends import _verify
from django.conf import settings
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen
import json
import datetime
from django.contrib.sessions.backends.db import SessionStore
from importlib import import_module
from authentication.models import WoollyUserType

def loggedCas(tree):
	print("[CAS LOGIN CALLBACK]")
class UpdatedCASBackend(CASBackend):
	"""
	An extension of the CASBackend to make it functionnable 
	with custom user models on user creation and selection
	"""

	def authenticate(self, ticket, service):
		"""
		Verifies CAS ticket and gets or creates User object
		NB: Use of PT to identify proxy
		"""
		print("_______________________ CAS Backend ________________")
		# SessionStore = import_module(settings.SESSION_ENGINE).SessionStore		# Use ?
		UserModel = get_user_model()
		username = _verify(ticket, service)
		if not username:
			return None

		try:
			user = UserModel.objects.get(login=username)
			# user = self.configure_user(user)
		except UserModel.DoesNotExist:
			# user will have an "unusable" password
			if settings.CAS_AUTO_CREATE_USER:
				user = UserModel.objects.create_user(username, '')
				# user = self.configure_user(user)
				# user.save()
			else:
				user = None
		return user

	def configure_user(self, user):
		"""
		Ginger overload
		"""
		print("gggggggggggggggggggiiiiiiiiiiiiiiiiinnnnger")
		params = {'key': settings.GINGER_KEY, }
		url = urljoin(settings.GINGER_SERVER_URL, user.login) + \
			'?' + urlencode(params)
		page = urlopen(url)
		response = page.read()
		json_data = json.loads(response.decode())

		user.first_name = json_data.get('prenom').capitalize()
		user.last_name = json_data.get('nom').capitalize()
		user.email = json_data.get('mail')
		if json_data.get('is_adulte'):
			user.birthdate = datetime.date.min
		else:
			user.birthdate = datetime.date.today
		if json_data.get('is_cotisant'):
			user.woollyusertype = WoollyUserType.objects.get(
				name=WoollyUserType.COTISANT)
		else:
			user.woollyusertype = WoollyUserType.objects.get(
				name=WoollyUserType.NON_COTISANT)
		return user
# """
