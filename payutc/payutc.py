import requests
import json
from datetime import date

class Payutc:

	def __init__(self, params):
		self.config  = {"url" : "https:/api.nemopay.net", "username":"username", "password":"password", "systemID" : "payutc", "async" : False, "app_key": params["apikey"], "fun_id":2, "sessionID":0,"logged_usr":"","loginMethod" : "payuser", "date" : date.today(),"debug":False }
		self.config["apikey"] = params["apikey"]

	def genericApiCall(self,service, method,data):
		response = ""
		url = "https://api.nemopay.net/services/" + service + "/" + method + "?system_id=" + self.config["systemID"]  + "&app_key=" + self.config["apikey"];
		if(self.config["sessionID"] != 0):
				url += "&sessionid=" + self.config["sessionID"]

		data = json.dumps(data)
		response = requests.post(url, data=data,headers={"Content-Type": "application/json"})
		return response.text

	def createTransaction(self,params):
		return self.genericApiCall("WEBSALE","createTransaction",{"items": params["itemsArray"], "fun_id": params["funId"], "mail":params["mail"], "return_url": params["returnUrl"], "callback_url": params["callbackUrl"]})

	def getTransactionInfo(self,params):
		return self.genericApiCall("WEBSALE","getTransactionInfo",{"fun_id": params["funId"],  "tra_id": params["traId"]})

	def payuser(self,params):
		resp =  self.genericApiCall("GESARTICLE","login2",{"login": params["login"], "password":params["password"]})
		resp = json.loads(resp)
		self.config["sessionID"] = resp["sessionid"]
		self.config["logged_usr"] = resp["username"]

	def setProduct(self,params):
		return self.genericApiCall("GESARTICLE","setProduct",{"name":params["name"],"parent":params["category"],"prix":params["price"],"stock":params["stock"],"alcool":params["alcool"],"image":params["image"],"image_path":params["image_path"],"fun_id":params["funId"],"obj_id":params["objId"] ,"tva":params["tva"], "cotisant":params["cotisant"]})

	def getAllMyRights(self):
		return self.genericApiCall("USERRIGHT","getAllMyRights",{})

	def getFundations(self):
		return self.genericApiCall("POSS3","getFundations",{})

	def cas(self,params):
		return self.genericApiCall("GESARTICLE","loginCas2",{"service":params["service"],"ticket":params["ticket"]})
		resp = json.loads(resp)
		self.config["sessionID"] = resp["sessionid"]
		self.config["logged_usr"] = resp["username"]