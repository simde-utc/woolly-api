from django.contrib.sessions.backends.db import SessionStore
from django.utils.crypto import get_random_string
from django.core.cache import cache

from authlib.specs.rfc7519 import JWT, JWTError
from authlib.client import OAuth2Session, OAuthException
import time

from woolly_api.settings import DEBUG, JWT_SECRET_KEY, JWT_TTL, OAUTH as OAuthConfig
from .helpers import get_jwt_from_request, find_or_create_user
from .models import User, UserType
from .serializers import UserSerializer


class OAuthAPI:
	"""
	Accès à l'API du portail des assos ou autre API OAuth
	Utile pour la connexion, la récupération des droits
	Methods:
		get_auth_url
		callback_and_create_session
		logout
		fetch_resource
	"""
	provider = 'portal'

	def __init__(self):
		"""
		OAuth2 and JWT Client initialisation
		"""
		config = OAuthConfig[self.provider]
		self.oauthClient = OAuth2Session(**config)

	def get_auth_url(self, redirect):
		"""
		Return authorization url
		"""
		# Get url and state from OAuth server
		url, state = self.oauthClient.authorization_url(
			OAuthConfig[self.provider]['authorize_url'])
		# Cache front url with state for 5mins
		cache.set(state, redirect, 300)
		return url

	def callback_and_create_session(self, request):
		"""
		Get token, user informations, store these and return a JWT
		"""
		try:
			# Get code and state from request
			code = request.GET.get('code', '')
			state = request.GET.get('state', '')

			# Get token from code
			oauthToken = self.oauthClient.fetch_access_token(
				OAuthConfig[self.provider]['access_token_url'], code=code)

			# Retrieve user infos from the Portal
			auth_user_infos = self.fetch_resource('user/?types=*')  # TODO restreindre

			# Find or create User
			user = find_or_create_user(auth_user_infos)

			request.session['user_id'] = user.pk
			request.session['portal_token'] = oauthToken

			# Get front redirection from cached state
			redirection = cache.get(state)
			cache.delete(state)

			if redirection == None:
				return 'root'

			return redirection

		except OAuthException as error:
			return {
				'error': 'OAuthException',
				'message': str(error)
			}

	def logout(self, jwt):
		"""
		Logout the user from Woolly and redirect to the provider's logout
		"""
		# Delete session

		# Redirect to logout
		return OAuthConfig[self.provider]['logout_url']

	def fetch_resource(self, query):
		"""
		Return infos from the API if 200 else an OAuthException
		"""
		resp = self.oauthClient.get(OAuthConfig[self.provider]['base_url'] + query)
		if resp.status_code == 200:
			return resp.json()
		elif resp.status_code == 404:
			raise OAuthException('Page not found')
		raise OAuthException('Unknown error')
