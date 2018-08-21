# from rest_framework_json_api import views
from rest_framework import status
from rest_framework.decorators import *
from django.urls import reverse

from rest_framework.response import Response
from django.http import JsonResponse
from core.helpers import errorResponse
from django.core.mail import EmailMessage

from authentication.auth import JWTAuthentication
from sales.permissions import IsOrderOwnerOrAdmin

from sales.serializers import OrderLineItemSerializer, OrderLineFieldSerializer
from sales.models import *
from .helpers import OrderValidator

from functools import reduce
from .services.payutc import Payutc
from woolly_api.settings import PAYUTC_KEY, PAYUTC_TRANSACTION_BASE_URL


# TODO
class PaymentView:
	pass


###################################################
# 		API Endpoints
###################################################

@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((IsOrderOwnerOrAdmin,))
def pay(request, pk):
	"""
	Permet le paiement d'une order
	Étapes:
		1. Retrieve Order
		2. Verify Order
		3. Process OrderLines
		4. Instanciate PaymentService
		5. Create Transaction
		6. Save Transaction info and redirect
	"""

	# 1. Retrieve Order
	try:
		order = Order.objects \
					.filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
					.select_related('sale', 'owner') \
					.get(pk=pk)
	except Order.DoesNotExist as e:
		return Response({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)

	# 2. Verify Order
	validator = OrderValidator(order)
	has_errors, message_list = validator.isValid()
	if has_errors:
		return orderErrorResponse(message_list)

	# 3. Process orderlines
	orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item')
	# Tableau pour Weez
	itemsArray = [ [int(orderline.item.nemopay_id), orderline.quantity] for orderline in orderlines ]
	if reduce(lambda acc, b: acc + b[1], itemsArray, 0) <= 0:
		return orderErrorResponse(["Vous devez avoir un nombre d'items commandés strictement positif."])

	# 4. Instanciate PaymentService
	payutc = Payutc({ 'app_key': PAYUTC_KEY })
	params = {
		'items': str(itemsArray),
		'mail': request.user.email,
		'fun_id': order.sale.association.fun_id,
		'return_url': request.GET.get('return_url', None),
		'callback_url': request.build_absolute_uri(reverse('pay-callback', kwargs={'pk': order.pk}))
	}

	# 5. Create Transaction
	transaction = payutc.createTransaction(params)
	if 'error' in transaction:
		print(transaction)
		return errorResponse(transaction['error']['message'])

	# 6. Save Transaction info and redirect
	order.status = OrderStatus.NOT_PAID.value
	order.tra_id = transaction['tra_id']
	order.save()

	# Redirect to transaction url
	resp = {
		'status': order.get_status_display(),
		'url': transaction['url']
	}
	return JsonResponse(resp, status=status.HTTP_200_OK)


@api_view(['GET'])
def pay_callback(request, pk):
	try:
		order = Order.objects \
					.select_related('sale__association').get(pk=pk)
					# .filter(status=OrderStatus.NOT_PAID.value) \
					# .prefetch_related('sale', 'orderlines', 'owner') \
	except Order.DoesNotExist as e:
		return errorResponse(str(e), status=status.HTTP_404_NOT_FOUND)

	payutc = Payutc({ 'app_key': PAYUTC_KEY })
	transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
	if 'error' in transaction:
		print(transaction)
		return errorResponse(transaction['error']['message'])

	return updateOrderStatus(order, transaction)



###################################################
# 		Helpers
###################################################

def getFieldDefaultValue(default, order):
	if default is None:
		return None
	return {
		'owner.first_name': order.owner.first_name,
		'owner.last_name': order.owner.last_name,
	}[default]

def orderErrorResponse(errors):
	return errorResponse('Erreur lors de la vérification de la commande.', errors, status.HTTP_400_BAD_REQUEST)


###################################################
# 		One Time Actions
###################################################

def updateOrderStatus(order, transaction):

	if transaction['status'] == 'A':
		order.status = OrderStatus.EXPIRED.value
		order.save()
		resp = {
			'status': OrderStatus.EXPIRED.name,
			'message': 'Votre commande a expiré.'
		}
	elif transaction['status'] == 'V':
		if order.status == OrderStatus.NOT_PAID.value:
			createOrderLineItemsAndFields(order)
			sendConfirmationMail(order)
		order.status = OrderStatus.PAID.value
		order.save()
		resp = {
			'status': OrderStatus.PAID.name,
			'message': 'Votre commande a été payée.'
		}
	else:
		resp = {
			'status': OrderStatus.NOT_PAID.name,
			'url': PAYUTC_TRANSACTION_BASE_URL + str(transaction['id'])
		}
	return JsonResponse(resp, status=status.HTTP_200_OK)

def createOrderLineItemsAndFields(order):
	# Create OrderLineItems
	orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item', 'orderlineitems').all()
	for orderline in orderlines:
		qte = orderline.quantity - len(orderline.orderlineitems.all())
		while qte > 0:
			orderlineitem = OrderLineItemSerializer(data = {
				'orderline': {
					'id': orderline.id,
					'type': 'orderlines'
				}
			})
			orderlineitem.is_valid(raise_exception=True)
			orderlineitem.save()

			# Create OrderLineFields
			for field in orderline.item.fields.all():
				orderlinefield = OrderLineFieldSerializer(data = {
					'orderlineitem': {
						'id': orderlineitem.data['id'],
						'type': 'orderlineitems'
					},
					'field': {
						'id': field.id,
						'type': 'fields'
					},
					'value': getFieldDefaultValue(field.default, order)
				})
				orderlinefield.is_valid(raise_exception=True)
				orderlinefield.save()
			qte -= 1

def sendConfirmationMail(order):
	# TODO : généraliser
	nb_places = reduce(lambda acc, orderline: acc + orderline.quantity, order.orderlines.all(), 0)
	message = "Bonjour " + order.owner.get_full_name() + ",\n\n" \
			+ "Nous vous confirmons avoir cotisé pour " + str(nb_places) + " place(s) " \
			+ "pour participer à la course de baignoires le dimanche 30 septembre.\n" \
			+ "Vous êtes désormais officiellement inscrit comme participant à la course !\n" \
			+ "Téléchargez vos billets ici : http://assos.utc.fr/baignoirutc/billetterie/commandes/" + str(order.pk) + "\n\n" \
			+ "Rendez vous le 30 septembre !!"

	email = EmailMessage(
		subject = "Confirmation Côtisation - Baignoires dans l'Oise",
		body = message,
		from_email = "sales@woolly.etu-utc.fr", # "woolly@assos.utc.fr",
		to = [order.owner.email],
		reply_to = ["baignoirutc@assos.utc.fr"],
	)
	email.send()


	# if order.status in OrderStatus.BUYABLE_STATUS_LIST.value:
		# Check on Weezevent if 
		# transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
		# updateOrderStatus(order, transaction)
