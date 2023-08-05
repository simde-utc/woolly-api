import requests
import json
from datetime import date


class Payutc:

	def __init__(self, params):
		self.config = {
			'username': None,
			'password': None,
			'systemID': 'payutc',
			'async': False,
			'app_key': params.get('app_key', None),
			'fun_id': params.get('fun_id', None),
			'sessionID': None,
			'logged_usr': None,
			'loginMethod': 'payuser',
			'date': date.today(),
			'debug': False,	# DEBUG
			# 'callback_url': params.get('callback_url', None)
		}
		self.config['url'] = "https://api.nemopay.be/" if self.config['debug'] else "https://api.nemopay.net/"

	def filterParams(self, params, keys):
		"""
		Filter params to only return keys
		"""
		data = { k: params.get(k, None) for k in keys }
		# Default values
		if 'fun_id' in keys and data['fun_id'] == None:
			data['fun_id'] = self.config['fun_id']
		return data

	def genericApiCall(self, service, method, data):
		response = ""
		url = self.config['url'] + "services/" + service + "/" + method \
				+ "?system_id=" + self.config["systemID"] + "&app_key=" + self.config["app_key"]
		if self.config["sessionID"] != None:
				url += "&sessionid=" + self.config["sessionID"]

		response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
		return json.loads(response.text)



	# ============================================
	# 	Web Transactions
	# ============================================

	def createTransaction(self, params):
		keys = ('items', 'mail', 'return_url', 'fun_id', 'callback_url')
		data = self.filterParams(params, keys)
		data['fun_id'] = str(data['fun_id'])
		print(json.dumps(data))
		f = open("/tmp/test.json", "a")
		f.write(json.dumps(data))
		return self.genericApiCall("WEBSALE", "createTransaction", data)

	def getTransactionInfo(self, params):
		data = self.filterParams(params, ('tra_id', 'fun_id'))
		return self.genericApiCall("WEBSALE", "getTransactionInfo", data)



	def payuser(self, params): # Cette methode se trouve dans tous les services
		resp = self.genericApiCall("WEBSALE", "login2", {"login": params["login"], "password": params["password"]})
		resp = json.loads(resp)
		self.config["sessionID"] = resp["sessionid"]
		self.config["logged_usr"] = resp["username"]

	def setProduct(self, params):
		keys = ('name', 'parent', 'prix', 'stock', 'alcool', 'image',
				'image_path', 'fun_id', 'obj_id', 'tva', 'cotisant')
		data = self.filterParams(params, keys)
		return self.genericApiCall("GESARTICLE", "setProduct", data)

	def getAllMyRights(self):
		return self.genericApiCall("USERRIGHT", "getAllMyRights", {}) # ?? USERRIGHT n'est plus dans l'API

	def getFundations(self):
		return self.genericApiCall("WEBSALE", "getFundations", {})
	# recupère les fondations sur lesquelles l'utilisateur est autorise

	def cas(self, params): # permet de connecter un utilisateur
		return self.genericApiCall("WEBSALE", "loginCas2", {"service": params["service"], "ticket": params["ticket"]})

