from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth as django_auth
from django.core.cache import cache

from authlib.client import OAuth2Session
from authlib.common.errors import AuthlibBaseError

from woolly_api.settings import OAUTH as OAuthConfig
from .helpers import find_or_create_user

OAUTH_TOKEN_NAME = 'oauth_token'
UserModel = django_auth.get_user_model()


class OAuthError(Exception):
	"""
	OAuth Error
	"""
	def __init__(self, message: str=None, response=None):
		if not message and response is not None:
			message = response.json().get('message', 'Unknown error')

		super().__init__(message)
		self.response = response

def get_user_from_request(request):
	"""
	Get the user from the request session
	Can debug logged user like this:
	> return UserModel(email='test@woolly.com') # DEBUG
	"""
	# Try to get the user logged in the request
	user = (getattr(request, '_request', request)).user
	if user.is_authenticated:
		return user

	# Get the user from the session
	user_id = request.session.get('user_id')
	if not user_id:
		return None
	try:
		return UserModel.objects.get(pk=user_id)
	except UserModel.DoesNotExist:
		raise AuthenticationFailed("user_id does not match a user")


class OAuthAPI:
	"""
	Accès à l'API du portail des assos ou autre API OAuth2
	Utile pour la connexion, la récupération des droits
	"""

	def __init__(self, provider: str='portal', config: dict=None, token: dict=None, session=None):
		"""
		OAuth2 Client initialisation
		"""
		self.provider = provider
		self.config = config or OAuthConfig[provider].copy()
		if token:
			self.config['token'] = token
		elif session:
			self.config['token'] = session.get(OAUTH_TOKEN_NAME)
		self.client = OAuth2Session(**self.config)

	def get_auth_url(self, redirection: str) -> str:
		"""
		Return authorization url
		"""
		# Get url and state from OAuth server
		url, state = self.client.create_authorization_url(self.config['authorize_url'])
		
		# Cache front url with state for 5mins
		cache.set(state, redirection, 300)
		return url

	def callback_and_create_session(self, request) -> str:
		"""
		Get token, user informations, store these and redirect
		"""
		# Get code and state from request
		code = request.GET['code']
		state = request.GET['state']

		# Get token from code
		try:
			token = self.client.fetch_access_token(self.config['access_token_url'], code=code)
		except AuthlibBaseError as error:
			raise OAuthError(error)

		# Retrieve user infos from the Portal
		auth_user_infos = self.fetch_resource('user/?types=*')  # TODO restreindre

		# Find or create User
		user = find_or_create_user(auth_user_infos)

		# Login user into Django and Create session
		request.user = user
		django_auth.login(request, user)
		request.session['user_id'] = user.pk
		request.session[OAUTH_TOKEN_NAME] = token

		# Get front redirection from cached state
		redirection = cache.get(state)
		cache.delete(state)
		return redirection or 'root'

	def logout(self, request, redirection: str=None):
		"""
		Logout the user from Woolly and redirect to the provider's logout
		"""
		# Revoke user token ??? POSSIBLE TODO
		# token = request.session.get(OAUTH_TOKEN_NAME)
		# if token:
		# 	self.client.revoke_token(url, token)

		# Logout from Django
		django_auth.logout(request)

		# Redirect to logout
		return self.config['logout_url']

	def fetch_resource(self, query: str):
		"""
		Return infos from the API if 200 else an OAuthError
		"""
		resp = self.client.get(self.config['base_url'] + query)
		if resp.status_code == 200:
			return resp.json()
		else:
			raise OAuthError(response=resp)


class OAuthBackend(ModelBackend):
	"""
	django.contrib.auth custom Backend with OAuth
	"""

	def authenticate(self, request, **kwargs):
		"""
		For rest_framework authentication
		"""
		return get_user_from_request(request)

	def get_user(self, user_id):
		try:
			return UserModel.objects.get(pk=user_id)
		except UserModel.DoesNotExist:
			return None

class OAuthAuthentication(SessionAuthentication):
	"""
	rest_framework custom Authentication with OAuth
	"""

	def authenticate(self, request, **kwargs):
		"""
		For rest_framework authentication
		"""
		user = get_user_from_request(request)
		if user:
			self.enforce_csrf(request)
			return (user, None)
		else:
			return None
