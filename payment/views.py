from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
# from django.utils import timezone
from functools import reduce

from rest_framework.response import Response
from django.http import JsonResponse
from core.helpers import errorResponse
from django.core.mail import EmailMessage

from sales.permissions import IsOrderOwnerOrAdmin
from sales.serializers import OrderLineItemSerializer, OrderLineFieldSerializer
from sales.models import *
from .helpers import OrderValidator

from woolly_api.settings import PAYUTC_KEY, PAYUTC_TRANSACTION_BASE_URL
from authentication.oauth import OAuthAuthentication
from .services.payutc import Payutc


# TODO
class PaymentView:
	pass


###################################################
# 		API Endpoints
###################################################

@api_view(['GET'])
@authentication_classes([OAuthAuthentication])
@permission_classes([IsOrderOwnerOrAdmin])
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
		# TODO ajout de la limite de temps
		order = Order.objects.filter(owner__pk=request.user.pk) \
					.filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
					.select_related('sale', 'owner') \
					.get(pk=pk)
	except Order.DoesNotExist as e:
		return Response({'message': str(e)}, status=status.HTTP_404_NOT_FOUND)

	# 2. Verify Order
	validator = OrderValidator(order, validateOnInit=True)
	if not validator.is_valid():
		return orderErrorResponse(validator.get_errors())

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
		'return_url': request.GET['return_url'],
		'callback_url': request.build_absolute_uri(reverse('pay-callback', kwargs={'pk': order.pk}))
	}

	# 5. Create Transaction
	transaction = payutc.createTransaction(params)
	if 'error' in transaction:
		print(transaction)
		# TODO Better feedback
		errors = (f"{k}: {m}" for k, m in transaction['error']['data'].items())
		return errorResponse(transaction['error']['message'], errors)

	# 6. Save Transaction info and redirect
	order.status = OrderStatus.NOT_PAID.value
	order.tra_id = transaction['tra_id']
	order.save()

	# Redirect to transaction url
	resp = {
		'status': order.get_status_display(),
		'url': transaction['url']
	}
	return Response(resp, status=status.HTTP_200_OK)


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
		# TODO parse error
		return errorResponse(transaction['error']['message'])

	return updateOrderStatus(order, transaction)



###################################################
# 		Helpers
###################################################

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
	return Response(resp, status=status.HTTP_200_OK)


# OrderLine
def getFieldDefaultValue(default, order):
	return {
		'owner.first_name': order.owner.first_name,
		'owner.last_name': order.owner.last_name,
	}.get(default, default)

def createOrderLineItemsAndFields(order):
	# Create OrderLineItems
	orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item', 'orderlineitems').all()
	total = 0
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
			total += 1
			qte -= 1
			
	return total

def sendConfirmationMail(order):
	# TODO : généraliser + markdown

	link_order = "http://assos.utc.fr/picasso/degustations/commandes/" + str(order.pk)
	message = "Bonjour " + order.owner.get_full_name() + ",\n\n" \
					+ "Votre commande n°" + str(order.pk) + " vient d'être confirmée.\n" \
					+ "Vous avez commandé:\n" \
					+ "".join([ " - " + str(ol.quantity) + " " + ol.item.name + "\n" for ol in order.orderlines.all() ]) \
					+ "Vous pouvez télécharger vos billets ici : " + link_order + "\n\n" \
					+ "Merci d'avoir utilisé Woolly"

	email = EmailMessage(
		subject="Woolly - Confirmation de commande",
		body=message,
		from_email="woolly@assos.utc.fr",
		to=[order.owner.email],
		reply_to=["woolly@assos.utc.fr"],
	)
	email.send()


	# if order.status in OrderStatus.BUYABLE_STATUS_LIST.value:
		# Check on Weezevent if 
		# transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
		# updateOrderStatus(order, transaction)
