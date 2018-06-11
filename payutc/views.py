from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json

from sales.models import OrderStatus
from .payutc import Payutc
from woolly_api import settings_confidential as confidentials


def createTransaction(request):
	params = {"apikey": confidentials.PAYUTC_KEY}
	mail = request.GET["mail"]
	funId = request.GET["funId"]
	orderlineId = request.GET['orderlineId']
	order = request.GET["order"]
	articles = request.body.decode('utf-8')
	p = Payutc(params)
	data = {
		"itemsArray": articles,
		"mail": mail,
		"returnUrl": "https://payutc.nemopay.net/",
		"funId": funId,
		# event_id pas d'event id
		"callbackUrl": "http://localhost:8000/payutc/returnTransaction?&funId="+funId+"orderlineId="+orderlineId,
		# "apikey":"d0ba09483a9ed6262d3924d7e7567d37"
		"apikey": confidentials.PAYUTC_KEY
	}
	response = json.loads(p.createTransaction(data))
	order.status = OrderStatus.VALIDATED
	#response = serializers.serialize('json',response)
	return JsonResponse(response)


def getTransactionInfo(request):
	params = {"apikey": confidentials.PAYUTC_KEY}
	funId = request.GET["funId"]
	order = request.GET["order"]
	data = {
		"traId": order.getTra_id(),
		"funId": funId
	}
	p = Payutc(params)
	state = p.getTransactionInfo(data)
	if state == 'V':
		order.status = OrderStatus.PAYED
	elif state == 'A':
		order.status = OrderStatus.CANCELLED
	elif state == 'W':
		order.status = OrderStatus.NOT_PAYED
	else:
		order.status = OrderStatus.NOT_PAYED
	return JsonResponse(state)


def setProduct(request):
	params = {"apikey": confidentials.PAYUTC_KEY}
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
	params = {"apikey": confidentials.PAYUTC_KEY}
	service = request.GET['service']
	ticket = request.GET['ticket']
	p = Payutc(params)
	p.cas({"service":service,
			"ticket":ticket})
	p.getFundations()
	return HttpResponse(response)

def returnTransaction(request):
	params = {"apikey": confidentials.PAYUTC_KEY}
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






