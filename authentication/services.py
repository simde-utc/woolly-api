from django.contrib.sessions.backends.db import SessionStore
from django.utils.crypto import get_random_string
from django.core.cache import cache

from authlib.client import OAuth2Session, OAuthException
import time

from woolly_api.settings import DEBUG, JWT_SECRET_KEY, JWT_TTL, OAUTH as OAuthConfig
from .helpers import get_jwt_from_request, find_or_create_user
from joserfc.jwt import decode as decode_jwt, encode as encode_jwt

class JWTClient:
	"""
	Authentification des utilisateurs entre le front et Woolly API
	Methods:
		retrieve_session_from_jwt
		get_claims
		validate
		create_jwt
		get_jwt_after_login
		refresh_jwt
		revoke_jwt
	"""
	def retrieve_session_from_jwt(self, jwt):
		"""
		"""
		# Get session id from jwt
		claims = self.get_claims(jwt)
		if 'error' in claims:
			return None
		session_key = claims['data']['session']

		# Retrieve session
		try:
			return SessionStore(session_key=session_key)
		except:
			return None

	def get_claims(self, jwt):
		"""
		Return the JSON content of a JWT
		"""
		try:
			return decode_jwt(jwt, JWT_SECRET_KEY)
		except:
			return {
				'error': 'InvalidJWT',
				'message': 'JWT is invalid'
			}

	def validate(self, jwt):
		"""
		Stock claims if jwt is valid, else raise a JWTError
		"""
		self.claims = decode_jwt(jwt, JWT_SECRET_KEY)

	def create_jwt(self, user_id, session_key):
		"""
		Create and return a new JWT with user_id and session_key
		All the data except user_id is kept in the session
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
		token = encode_jwt(header, payload, JWT_SECRET_KEY)
		return {
			'token_type': 'Bearer',
			'token': token,
			'expires_at': exp
		}

	def get_jwt_after_login(self, code):
		"""
		Return JWT to the client after it logged in and got a random code to the session
		"""
		# WARNING : Backdoor in Debug mode for easier testing
		if DEBUG == True and code[:8] == 'DEBUG - ':
			print("\n##########################################")
			print("   WARNING --- The JWT backdoor is used   ")
			print("##########################################\n")

			# Create fake session
			user_id = int(code[8:])
			session = SessionStore()
			session['portal_token'] = None
			session['user_id'] = user_id
			session.create()

			return self.create_jwt(user_id, session.session_key)

		# Retrieve session_key from random code
		session_key = cache.get(code)
		cache.delete(code)

		if session_key == None:
			return {
				'error': 'InvalidSession',
				'message': 'Session cannot be found. You may have taken too much time login, try again.'
			}

		# Retrieve session and create JWT from its infos
		session = SessionStore(session_key = session_key)
		return self.create_jwt(session['user_id'], session_key)
	
	def refresh_jwt(self, jwt):
		"""
		Return a new JWT from an old one
		"""
		try:
			self.validate(jwt)
		except JWTError as error:
			return {
				'error': 'JWTError',
				'message': str(error)
			}
		self.revoke_jwt(jwt)
		return self.create_jwt(self.claims['user_id'], self.claims['session_key'])

	def revoke_jwt(self, jwt):
		# TODO
		pass
	

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

	def callback_and_create_session(self, request):
		"""
		Get token, user informations, store these and return a JWT 
		"""
		try:
			# Get code and state from request
			code = request.GET.get('code', '')
			state = request.GET.get('state', '')

			# Get token from code
			oauthToken = self.oauthClient.fetch_access_token(OAuthConfig[self.provider]['access_token_url'], code=code)

			# Retrieve user infos from the Portal
			auth_user_infos = self.fetch_resource('user/?types=*') # TODO restreindre

			# Find or create User
			user = find_or_create_user(auth_user_infos)

			# TODO : gestion exceptions

			# Store portal token linked to user id
			# TODO : check expiration and optimize
			session = SessionStore()
			session['portal_token'] = oauthToken
			session['user_id'] = user.id
			session.create()

			# Get front redirection from cached state
			redirection = cache.get(state)
			cache.delete(state)

			# TODO Connexion par l'API Django
			if redirection == None:
				# login(request, user)
				return 'root'

			# Cache session_key to retrieve it for the jwt
			code = get_random_string(length=32)
			cache.set(code, session.session_key, 300)

			return redirection + '?code=' +  code

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
		session = self.jwtClient.retrieve_session_from_jwt(jwt)
		if session:
			session.delete()

		# Revoke JWT
		self.jwtClient.revoke_jwt(jwt)

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


