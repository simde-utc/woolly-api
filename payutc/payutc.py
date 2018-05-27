import requests
import json
from datetime import date


class Payutc:

	def __init__(self, params):
		self.config = {
			'url': 'https:/api.nemopay.net',
			'username': 'username',
			'password': 'password',
			'systemID': 'payutc',
			'async': False,
			'app_key': params['apikey'],
			'fun_id': 2,
			'sessionID': 0,
			'logged_usr': '',
			'loginMethod': 'payuser',
			'date': date.today(),
			'debug': False
		}

	def genericApiCall(self, service, method, data):
		response = ""
		url = "https://api.nemopay.net/services/" + service + "/" + method + "?system_id=" + self.config["systemID"] + "&app_key=" + self.config["apikey"]
		if self.config["sessionID"] != 0:
				url += "&sessionid=" + self.config["sessionID"]

		data = json.dumps(data)
		response = requests.post(url, data=data, headers={"Content-Type": "application/json"})
		return response.text

	def createTransaction(self, params):
		return self.genericApiCall("WEBSALE", "createTransaction", {"items": params["itemsArray"], "mail": params["mail"], "return_url": params["returnUrl"], "fun_id": params["funId"], "callback_url": params["callbackUrl"]})

	def getTransactionInfo(self, params):
		return self.genericApiCall("WEBSALE", "getTransactionInfo", {"tra_id": params["traId"], "fun_id": params["funId"]})

	def payuser(self, params): # Cette methode se trouve dans tous les services
		resp = self.genericApiCall("WEBSALE", "login2", {"login": params["login"], "password": params["password"]})
		resp = json.loads(resp)
		self.config["sessionID"] = resp["sessionid"]
		self.config["logged_usr"] = resp["username"]

	def setProduct(self,params):
		return self.genericApiCall("GESARTICLE", "setProduct", {"name":params["name"], "parent": params["category"], "prix": params["price"], "stock":params["stock"], "alcool": params["alcool"], "image": params["image"], "image_path": params["image_path"], "fun_id":params["funId"], "obj_id": params["objId"], "tva":params["tva"], "cotisant": params["cotisant"]})

	def getAllMyRights(self):
		return self.genericApiCall("USERRIGHT", "getAllMyRights", {}) # ?? USERRIGHT n'est plus dans l'API

	def getFundations(self):
		return self.genericApiCall("WEBSALE", "getFundations", {})
	# recupère les fondations sur lesquelles l'utilisateur est autorise

	def cas(self, params): # permet de connecter un utilisateur
		return self.genericApiCall("WEBSALE", "loginCas2", {"service": params["service"], "ticket": params["ticket"]})
