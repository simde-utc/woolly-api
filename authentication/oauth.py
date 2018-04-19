from authlib.client import OAuth2Session, OAuthException
from woolly_api.settings import PORTAL as PortalConfig

import json
from pprint import pprint


class PortalAPI:

	def __init__(self):
		self.oauth = OAuth2Session(**PortalConfig['oauth'])

		
	def get_authorize_url(self):
		uri, state = self.oauth.authorization_url(PortalConfig['oauth']['authorize_url'])
		return {
			'url': uri,
			'state': state
		} 


	def get_auth_session(self, code):
		try:
			token = self.oauth.fetch_access_token(PortalConfig['oauth']['access_token_url'], code=code, verify=None)
			self.store_auth_token(token)
			return {
				'token': token
			} 
		except OAuthException as error:
			return {
				'error': 'OAuthException',
				'message': str(error)
			}

	def store_auth_token(self, token):
		pass

	def fetch_resource(self, req):
		pass
		# return token = get_user_token_from_db(request.user)


