from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json
from .payutc import Payutc
from django.contrib.sessions.backends.db import SessionStore
from woolly_api import settings


def createTransaction(request):
	#for key, value in request.session.items(): 
	#	print('{} => {}'.format(key, value))
	params = { "apikey": PAYUTC_KEY }
	mail = request.GET["mail"]
	funId = request.GET["funId"]
	orderlineId = request.GET['orderlineId']
	articles = request.body.decode('utf-8')
	p = Payutc(params)
	data  =  {
		"itemsArray": articles,
		"funId": funId,
		"mail" :mail,
		"returnUrl": "https://payutc.nemopay.net/",
		# TODO : sale...
		"callbackUrl" : "http://localhost:8000/payutc/returnTransaction?&funId="+funId+"orderlineId="+orderlineId,
		"apikey":"d0ba09483a9ed6262d3924d7e7567d37"
	}
	response =  json.loads(p.createTransaction(data))
	#response = serializers.serialize('json',response)
	return JsonResponse(response)

def setProduct(request):
	params = { "apikey": PAYUTC_KEY }
	name = request.GET['name']
	category = request.GET["category"]
	price = request.GET['price']
	funId = request.GET['funId']
	service = request.GET['service']
	ticket = request.GET['ticket']
	p = Payutc(params)
	p.cas({ "service": service, "ticket": ticket })
	dataproduct = {
		"name": name,
		"category": category,
		"price": price,
		"funId": funId,
		"stock": 0,
		"cotisant": 1,
		"alcool": 0,
		"tva": "0.00",
		"image": None,
		"image_path": "",
	 	"objId": None
	 }
	response = p.setProduct(dataproduct)
	p.getFundations()
	return HttpResponse(response)

def getFundations(request):
	params = { "apikey": PAYUTC_KEY }
	service = request.GET['service']
	ticket = request.GET['ticket']
	p = Payutc(params)
	p.cas({"service":service,
			"ticket":ticket})
	p.getFundations()
	return HttpResponse(response)

def returnTransaction(request):
	params = { "apikey": PAYUTC_KEY }
	funId = request.GET['funId']
	oderlineId = request.GET['orderlineId']
	transactionId = request.query
	transactionId= int(float(transactionId))
	p = Payutc(params)
	data =   {"traId":transactionId,"funId": funId,}
	response= json.loads(p.getTransactionInfo(data))
	statutTrans = response['status']
	if statutTrans == 'V': 
		print("v")
		#do some stuff with the orderlineId
	else:
		print("not v")
		#do other stuff with the orderlineId






