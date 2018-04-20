from authlib.client import OAuth2Session, OAuthException
from woolly_api.settings import JWT_SECRET_KEY, JWT_TTL, OAUTH as OAuthConfig
from .models import WoollyUser
from .serializers import WoollyUserSerializer
from django.contrib.sessions.backends.db import SessionStore

from authlib.specs.rfc7519 import JWT, JWTError

import json
from pprint import pprint
import time



class OAuthAPI:
	"""
	Accès à l'API du portail des assos
	Utile pour la connexion, la récupération des droits
	"""
	provider = 'portal'
	user = None
	oauthToken = None

	def __init__(self):
		"""
		OAuth2 and JWT Client initialisation
		"""
		self.oauthClient = OAuth2Session(**OAuthConfig[self.provider])
		self.jwtClient = JWTClient()

		
	def login(self):
		"""
		Return authorization url
		"""
		url, state = self.oauthClient.authorization_url(OAuthConfig[self.provider]['authorize_url'])
		return url


	def get_auth_session(self, code):
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
			# TODO : check expiration
			session = SessionStore()
			session['portal_token'] = self.oauthToken
			session['user_id'] = self.user.id
			session.create()
			
			# Create JWT token linked to the session key and return it
			jwt = self.jwtClient.get_jwt(self.user.id, session.session_key)
			return jwt

			return WoollyUserSerializer(user).data
		except OAuthException as error:
			return {
				'error': 'OAuthException',
				'message': str(error)
			}
	
	def logout(self, jwt):
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


	def retrieve_session_from_jwt(self, jwt):
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


class JWTClient(JWT):

	def validate(self, jwt):
		self.claims = self.decode(jwt, JWT_SECRET_KEY)
		self.claims.validate()
		# raise a JWTError if not valid

	def get_jwt(self, user_id, session_key):
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

	def revoke_jwt(self, jwt):
		# TODO
		return None

	def refresh_jwt(self, jwt):
		try:
			self.validate(jwt)
		except JWTError as error:
			return {
				'error': 'JWTError',
				'message': str(JWTError)
			}
		self.revoke_jwt(jwt)
		return self.get_jwt(self.claims['user_id'], self.claims['session_key'])

	def get_claims(self, jwt):
		try:
			self.validate(jwt)
			return self.claims
		except JWTError as error:
			return {
				'error': 'JWTError',
				'message': str(JWTError)
			}

