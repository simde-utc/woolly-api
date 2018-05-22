from django.contrib.sessions.backends.db import SessionStore
from django.utils.crypto import get_random_string
from django.core.cache import cache

from authlib.specs.rfc7519 import JWT, JWTError
from authlib.client import OAuth2Session, OAuthException
import time

from woolly_api.settings import JWT_SECRET_KEY, JWT_TTL, OAUTH as OAuthConfig
from .models import WoollyUser
from .serializers import WoollyUserSerializer

# from .backends import JWTBackend
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model




class OAuthAPI:
	"""
	Accès à l'API du portail des assos
	Utile pour la connexion, la récupération des droits
	"""
	provider = 'portal'
	user = None
	oauthToken = None

	def __init__(self,redirection=''):
		"""
		OAuth2 and JWT Client initialisation
		"""
		config = OAuthConfig[self.provider]
		self.oauthClient = OAuth2Session(**config)
		self.jwtClient = JWTClient()

		
	def get_auth_url(self, redirect):
		"""
		Return authorization url
		"""
		# Get url and state from OAuth server
		url, state = self.oauthClient.authorization_url(OAuthConfig[self.provider]['authorize_url'])

		# Cache front url with state for 5mins
		cache.set(state, redirect, 300)

		return url


	def callback_and_create_session(self, code, state):
		"""
		Get token, user informations, store these and return a JWT 
		"""
		try:
			# Get token from code
			self.oauthToken = self.oauthClient.fetch_access_token(OAuthConfig[self.provider]['access_token_url'], code=code)

			# Retrieve user infos from the Portal
			auth_user = self.fetch_resource('user/')

			# Find or create User
			self.user = self.find_or_create_user(auth_user)

			# Store portal token linked to user id
			# TODO : check expiration and optimize
			session = SessionStore()
			session['portal_token'] = self.oauthToken
			session['user_id'] = self.user.id
			session.create()

			# Get front redirection from cached state
			redirection = cache.get(state)
			cache.delete(state)

			# TODO gérer ce cas
			if redirection == None:
				return 'auth.login'

			# Cache session_key to retrieve it for the jwt
			cache_key = get_random_string(length=32)
			cache.set(cache_key, session.session_key, 300)

			return redirection + '?code=' +  cache_key

		except OAuthException as error:
			return {
				'error': 'OAuthException',
				'message': str(error)
			}

	def get_jwt_after_login(self, code):
		"""
		Return JWT to the client after it logged in and got a random code to the session
		"""
		# Retrieve session_key from random code
		session_key = cache.get(code)
		cache.delete(code)
		# TODO gestion erreur
		if session_key == None:
			return {}

		# Retrieve session and create JWT from its infos
		session = SessionStore(session_key=session_key)
		return self.jwtClient.get_jwt(session['user_id'], session_key)
	
	def logout(self, jwt):
		"""
		Logout the user in Woolly and redirect to the provider's logout
		"""

		# Delete cached properties
		self.oauthToken = None
		self.user = None

		# Delete session
		session = retrieve_session_from_jwt(jwt)
		session.delete()

		# Revoke JWT
		self.jwtClient.revoke_jwt(jwt)

		# Redirect to logout
		return OAuthConfig[self.provider]['logout']


	# =========================================
	# 		Utils
	# =========================================


	def retrieve_session_from_jwt(self, jwt):
		"""
		"""
		# Get session id from jwt
		claims = self.jwtClient.get_claims(jwt)
		if 'error' in claims:
			return None
		session_key = claims['data']['session']

		# Retrieve session
		try:
			return SessionStore(session_key=session_key)
		except:
			return None


	def find_or_create_user(self, auth_user):
		"""
		Fetch or create user in Woolly database from Portal infos (email)
		"""
		try:
			# Try to find user
			user = WoollyUser.objects.get(email = auth_user['email'])		# TODO replace
		except WoollyUser.DoesNotExist:
			# Create user
			print("create")
			serializer = WoollyUserSerializer(data = {
				'email': auth_user['email'],
				'first_name': auth_user['firstname'],
				'last_name': auth_user['lastname'],
				# TODO add login ...
				# 'login': auth_user['login'],		# TODO add login in with for Portail
				# 'woollyusertype': '',
				# 'associations': '',
				# 'birthdate': ''
			})
			if not serializer.is_valid():
				return serializer.errors
			user = serializer.save()
		return user


	def fetch_resource(self, req):
		"""
		Return infos from the API if 200 else an OAuthException
		"""
		resp = self.oauthClient.get(OAuthConfig[self.provider]['base_url'] + req)
		if resp.status_code == 200:
			return resp.json()
		elif resp.status_code == 404:
			raise OAuthException('Page not found')
		raise OAuthException('Unknown error')

		# return token = get_user_token_from_db(request.user)



# TODO ['data partout']
class JWTClient(JWT):
	"""
	JWT Client used to authenticate users
	"""
	def get_user_id(self, jwt):
		try:
			self.validate(jwt)
			return self.claims['data']['user_id']
		except JWTError as error:
			return None

	def get_claims(self, jwt):
		"""
		Return the JSON content of a JWT
		"""
		try:
			self.validate(jwt)
			return self.claims
		except JWTError as error:
			return {
				'error': 'JWTError',
				'message': str(JWTError)
			}

	def validate(self, jwt):
		"""
		Stock claims if jwt is valid, else raise a JWTError
		"""
		self.claims = self.decode(jwt, JWT_SECRET_KEY)
		self.claims.validate()

	def get_jwt(self, user_id, session_key):
		"""
		Create and return a new JWT with user_id and session_key
		"""
		exp = int(time.time()) + JWT_TTL
		header = {
			'alg': 'HS256',
			'typ': 'JWT'
		}
		payload = {
			'iss': 'woolly_api',
			'exp': exp,
			'data': {
				'user_id': 	user_id,
				'session': 	session_key,
			}
		}
		token = self.encode(header, payload, JWT_SECRET_KEY).decode('utf-8')
		return {
			'token_type': 'Bearer',
			'token': token,
			'expires_at': exp
		}

	def refresh_jwt(self, jwt):
		"""
		Return a new JWT from an old one
		"""
		try:
			self.validate(jwt)
		except JWTError as error:
			return {
				'error': 'JWTError',
				'message': str(JWTError)
			}
		self.revoke_jwt(jwt)
		return self.get_jwt(self.claims['user_id'], self.claims['session_key'])

	def revoke_jwt(self, jwt):
		# TODO
		return None

def get_jwt_from_request(request):
	try:
		jwt = request.META['HTTP_AUTHORIZATION']
	except KeyError:
		return None
	if not jwt or jwt == '':
		return None
	return jwt[7:]		# substring : Bearer ...


class JWTBackend():
	def __init__(self):
		self.jwtClient = JWTClient()
		# One-time configuration and initialization.

	def authenticate(self, request):
		print("AUTHENTICATE")
		# Get JWT from request header
		try:
			jwt = request.META['HTTP_AUTHORIZATION']
		except KeyError:
			return AnonymousUser
		if not jwt or jwt == '':
			return AnonymousUser
		jwt = jwt[7:]		# substring : Bearer ...

		# Get user id
		user_id = self.jwtClient.get_user_id(jwt)
		print(user_id)
		if user_id == None:
			return AnonymousUser

		# Try logging user
		UserModel = get_user_model()
		try:
			return UserModel.objects.get(id=user_id)
		except UserModel.DoesNotExist:
			return AnonymousUser

class JWTMiddleware:
	"""
	Middleware to log user from JWT into request.user
	"""
	def __init__(self, get_response):
		self.get_response = get_response
		self.backend = JWTBackend()

	def __call__(self, request):
		request.user = self.backend.authenticate(request)
		return self.get_response(request)


