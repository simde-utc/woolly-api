from authlib.client import OAuth2Session, OAuthException
from woolly_api.settings import PORTAL as PortalConfig
from .models import WoollyUser
from .serializers import WoollyUserSerializer

import json
from pprint import pprint


class PortalAPI:
	token = None
	user = None

	def __init__(self):
		"""
		Initialisation du client OAuth2
		"""
		self.oauth = OAuth2Session(**PortalConfig['oauth'])

		
	def get_authorize_url(self):
		"""
		Récupération de l'URL d'authorisation
		"""
		uri, state = self.oauth.authorization_url(PortalConfig['oauth']['authorize_url'])
		return {
			'url': uri,
			'state': state
		} 


	def get_auth_session(self, code):
		"""
		Get token, user informations, store these and return a jwt 
		"""
		try:
			# Get token from code
			self.token = self.oauth.fetch_access_token(PortalConfig['oauth']['access_token_url'], code=code)
			# Retrieve user infos
			auth_user = self.fetch_resource('user/')
			# Find or create User
			user = self.find_or_create_user(auth_user)

			return WoollyUserSerializer(user).data
		except OAuthException as error:
			return {
				'error': 'OAuthException',
				'message': str(error)
			}



	def find_or_create_user(self, auth_user):
		"""
		Fetch or create user in Woolly database from Portal infos (email)
		"""
		pp(auth_user, "auth_user")
		try:
			user = WoollyUser.objects.get(email = 'azdazd')
			print("get")
		except WoollyUser.DoesNotExist:
			user = WoollyUserSerializer.create(**{
				'email': auth_user['email'],
				'first_name': auth_user['firstname'],
				'last_name': auth_user['lastname'],
			})
				# 'login': auth_user['login'],		# TODO add login in with for Portail
				# 'woollyusertype': '',
				# 'associations': '',
				# 'birthdate': ''
				

			print("create")
		pp(user, "retrieved user")
		return user


	def store_auth_token(self, token):

		pass

	def fetch_resource(self, req):
		"""
		Return infos from the API if 200 else an OAuthException
		"""
		resp = self.oauth.get(PortalConfig['oauth']['base_url'] + req)
		if resp.status_code == 200:
			return resp.json()
		elif resp.status_code == 404:
			raise OAuthException('Page not found')
		raise OAuthException('Unknown error')

		# return token = get_user_token_from_db(request.user)


# =========================
# 	DEBUG
# =========================

from django.core import serializers

def pp(obj, text = None):
	if text:
		print(text)
	pprint(obj)
	# print(serializers.serialize('json', obj))