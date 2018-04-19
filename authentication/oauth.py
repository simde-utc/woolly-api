from rauth import OAuth2Service
from woolly_api.settings import PORTAL as PortalConfig
from pprint import pprint
import json


class PortalAPI:

	def __init__(self):
		self.oauth = OAuth2Service(**PortalConfig['oauth'])

	def get_authorize_url(self):
		"""
		Retourne l'url d'authorize
		"""
		params = {
			'response_type': 'code',
			'redirect_uri': PortalConfig['callback'],
			'scope': 'user-get-assos-done-now',
		}
		resp = {
			'url': self.oauth.get_authorize_url(**params)
		} 
		return resp

	def decoder(self, data):
		parsed = json.loads(data.decode('utf-8'))
		pprint(type(parsed))
		pprint(parsed)
		if ('error' in parsed):
			raise Exception(parsed['message'])
		# pprint(parsed['access_token'])
		return parsed

	def get_auth_session(self, code):
		print('geeeeeeeeeeeeeeeeeeeeet')
		print(code)
		data = {
			'code': code,
			'grant_type': 'authorization_code',
			'redirect_uri': 'http://localhost:8000/auth/callback2'
		}
		try:
			x = self.oauth.get_access_token(data=data, decoder=self.decoder)
			return x
		except Exception as e:
			print("Exxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
			pprint(e)
			return {'error': e}
