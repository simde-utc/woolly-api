from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.core.cache import cache

from authlib.client import OAuth2Session
from authlib.common.errors import AuthlibBaseError

from woolly_api.settings import OAUTH as OAuthConfig
from django.contrib.auth import get_user_model
from .helpers import find_or_create_user

UserModel = get_user_model()


class OAuthAPI(SessionAuthentication):
	"""
	Accès à l'API du portail des assos ou autre API OAuth2
	Utile pour la connexion, la récupération des droits
	"""

	def __init__(self, provider: str='portal', config: dict=None):
		"""
		OAuth2 Client initialisation
		"""
		self.provider = provider
		self.config = config or OAuthConfig[provider]
		self.oauth_client = OAuth2Session(**self.config)

	def get_user_from_request(self, request):
		"""
		Get the user from the request session
		"""
		# user = getattr(request._request, 'user', None) # TODO
		if request._request.user.is_authenticated:
			return request._request.user

		user_id = request.session.get('user_id')
		if not user_id:
			return None
		try:
			return UserModel.objects.get(pk=user_id)
		except UserModel.DoesNotExist:
			raise AuthenticationFailed("user_id does not match a user")

	def authenticate(self, request, **kwargs):
		"""
		For rest_framework authentication
		"""
		user = self.get_user_from_request(request)
		if user:
			# Attach user and CSRF token to the request
			request.user = user
			self.enforce_csrf(request)
			return (user, None)
		else:
			return None


	def get_auth_url(self, redirect):
		"""
		Return authorization url
		"""
		# Get url and state from OAuth server
		url, state = self.oauth_client.create_authorization_url(self.config['authorize_url'])
		
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
			oauthToken = self.oauth_client.fetch_access_token(self.config['access_token_url'], code=code)

			# Retrieve user infos from the Portal
			auth_user_infos = self.fetch_resource('user/?types=*')  # TODO restreindre

			# Find or create User
			user = find_or_create_user(auth_user_infos)

			# Login and Create session
			request.user = user
			request.session['user_id'] = user.pk
			request.session['portal_token'] = oauthToken

			# Get front redirection from cached state
			redirection = cache.get(state)
			cache.delete(state)

			return redirection or 'root'

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
		resp = self.oauth_client.get(self.config['base_url'] + query)
		if resp.status_code == 200:
			return resp.json()
		elif resp.status_code == 404:
			raise AuthlibBaseError('Page not found')
		raise AuthlibBaseError('Unknown error')
