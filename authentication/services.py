from django.contrib.sessions.backends.db import SessionStore
from django.utils.crypto import get_random_string
from django.core.cache import cache

from authlib.client import OAuth2Session
from authlib.common.errors import AuthlibBaseError
import time

from woolly_api.settings import DEBUG, OAUTH as OAuthConfig
from .helpers import find_or_create_user
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

	def __init__(self, provider: str='portal', config: dict=None):
		"""
		OAuth2 Client initialisation
		"""
		self.provider = provider
		self.config = config or OAuthConfig[provider]
		self.oauthClient = OAuth2Session(**self.config)

	def get_auth_url(self, redirect):
		"""
		Return authorization url
		"""
		# Get url and state from OAuth server
		url, state = self.oauthClient.create_authorization_url(self.config['authorize_url'])
		
		# Cache front url with state for 5mins
		cache.set(state, redirect, 300)
		return url

	def callback_and_create_session(self, request):
		"""
		Get token, user informations, store these and redirect
		"""
		try:
			# Get code and state from request
			code = request.GET.get('code', '')
			state = request.GET.get('state', '')

			# Get token from code
			oauthToken = self.oauthClient.fetch_access_token(self.config['access_token_url'], code=code)

			# Retrieve user infos from the Portal
			auth_user_infos = self.fetch_resource('user/?types=*')  # TODO restreindre

			# Find or create User
			user = find_or_create_user(auth_user_infos)

			# Create session
			request.session['user_id'] = user.pk
			request.session['portal_token'] = oauthToken

			# Get front redirection from cached state
			redirection = cache.get(state)
			cache.delete(state)

			if redirection == None:
				return 'root'

			return redirection

		except AuthlibBaseError as error:
			return {
				'error': 'AuthlibBaseError',
				'message': str(error)
			}

	def logout(self, request, redirection=None):
		"""
		Logout the user from Woolly and redirect to the provider's logout
		"""
		# Delete session
		request.session.flush()

		# Redirect to logout
		return self.config['logout_url']

	def fetch_resource(self, query):
		"""
		Return infos from the API if 200 else an AuthlibBaseError
		"""
		resp = self.oauthClient.get(self.config['base_url'] + query)
		if resp.status_code == 200:
			return resp.json()
		elif resp.status_code == 404:
			raise AuthlibBaseError('Page not found')
		raise AuthlibBaseError('Unknown error')
