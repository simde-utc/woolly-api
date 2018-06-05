from django.utils import timezone
from functools import reduce

# from rest_framework_json_api import views
from rest_framework.response import Response
from rest_framework import permissions, status
from django.http import JsonResponse
from django.urls import reverse

from core.permissions import *
from sales.models import *
from sales.serializers import *
from sales.permissions import *

from .services.payutc import Payutc
from woolly_api.settings import PAYUTC_KEY, PAYUTC_TRANSACTION_BASE_URL
from rest_framework.decorators import *
from authentication.auth import JWTAuthentication


# TODO
class PaymentView:
	pass

@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((permissions.IsAuthenticated, IsOwner))
def pay(request, pk):
	# Récupération de l'Order
	try:
		# TODO ajout de la limite de temps
		order = Order.objects.filter(owner=request.user) \
					.prefetch_related('sale').prefetch_related('orderlines').prefetch_related('owner') \
					.get(pk=pk)
	except Order.DoesNotExist as e:
		return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

	# Payutc Instance
	payutc = Payutc({ 'app_key': PAYUTC_KEY })

	if order.status == OrderStatus.NOT_PAYED.value:
		transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
		changeOrderStatus(order, transaction)

	# Verifications
	errors = verifyOrder(order, request.user)
	if len(errors) > 0:
		return orderErrorResponse(errors)

	# Retrieve orderlines
	orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item').all()

	# Add items
	itemsArray = []
	for orderline in orderlines:
		itemsArray.append([int(orderline.item.nemopay_id), orderline.quantity])
	if reduce(lambda acc, b: acc + b[1], itemsArray, 0) <= 0:
		return orderErrorResponse(["Vous devez avoir un nombre d'items commandé strictement positif."])

	# Create Payutc params
	params = {
		'items': str(itemsArray),
		'mail': request.user.email,
		'fun_id': order.sale.association.fun_id,
		'return_url': request.GET.get('return_url', None),
		'callback_url': request.build_absolute_uri(reverse('pay-callback', kwargs={'pk': order.pk}))
	}

	# Create transaction
	transaction = payutc.createTransaction(params)
	if 'error' in transaction:
		return Response({'message': transaction['error']['message']}, status=status.HTTP_400_BAD_REQUEST)

	# Save transaction info
	order.status = OrderStatus.NOT_PAYED.value
	order.tra_id = transaction['tra_id']
	order.save()

	# Redirect to transaction url
	resp = {
		'status': 'NOT_PAYED',
		'url': transaction['url']
	}
	return JsonResponse(resp, status=status.HTTP_200_OK)


@api_view(['GET'])
def pay_callback(request, pk):
	print("========= pay_callback =========")
	try:
		order = Order.objects \
					.prefetch_related('sale').prefetch_related('orderlines').prefetch_related('owner') \
					.get(pk=pk)
	except Order.DoesNotExist as e:
		return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

	payutc = Payutc({ 'app_key': PAYUTC_KEY })
	transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
	return changeOrderStatus(order, transaction)




def verifyOrder(order, user):
	# Error bag to store all error messages
	errors = list()

	# Check active & date
	if order.sale.is_active == False:
		errors.append("La vente n'est pas disponible.")
	now = timezone.now()
	if now < order.sale.begin_at:
		errors.append("La vente n'a pas encore commencé.")
	if now > order.sale.end_at:
		errors.append("La vente est terminée.")
	# Checkpoint
	if len(errors) > 0:
		return errors

	# OrderStatus considered as not canceled
	statusList = [OrderStatus.AWAITING_VALIDATION.value, OrderStatus.VALIDATED.value,
					OrderStatus.NOT_PAYED.value, OrderStatus.PAYED.value]

	# Fetch orders made by the user
	userOrders = Order.objects \
					.filter(owner__pk=user.pk, sale__pk=order.sale.pk, status__in=statusList) \
					.exclude(pk=order.pk) \
					.prefetch_related('orderlines')
	# Count quantity bought by user
	quantityByUser = dict()
	quantityByUserTotal = 0
	for userOrder in userOrders:
		for orderline in userOrder.orderlines.all():
			quantityByUser[orderline.item.pk] = orderline.quantity + quantityByUser.get(orderline.item.pk, 0)
			quantityByUserTotal += orderline.quantity

	# Fetch all orders of the sale
	saleOrders = Order.objects \
					.filter(sale__pk=order.sale.pk, status__in=statusList) \
					.exclude(pk=order.pk) \
					.prefetch_related('orderlines')
	# Count quantity bought by sale
	quantityBySale = dict()
	quantityBySaleTotal = 0
	for saleOrder in saleOrders:
		for orderline in saleOrder.orderlines.all():
			quantityBySale[orderline.item.pk] = orderline.quantity + quantityBySale.get(orderline.item.pk, 0)
			quantityBySaleTotal += orderline.quantity


	# Verify quantity left by sale
	if order.sale.max_item_quantity != None:
		if order.sale.max_item_quantity < quantityBySaleTotal + quantityByUserTotal:
			errors.append("Il reste moins de {} items pour cette vente.".format(quantityByUserTotal))

	# Check for each orderlines
	for orderline in order.orderlines.filter(quantity__gt=0).all():

		# Verif max_per_user // quantity
		if orderline.quantity > orderline.item.max_per_user:
			errors.append("Vous ne pouvez prendre que {} {} par personne." \
				.format(orderline.item.max_per_user, orderline.item.name))

		# Verif max_per_user // user orders
		if quantityByUser.get(orderline.item.pk, 0) + orderline.quantity > orderline.item.max_per_user:
			errors.append("Vous avez déjà pris {} {} sur un total de {} par personne." \
				.format(quantityByUser.get(orderline.item.pk, 0), orderline.item.name, orderline.item.max_per_user))

		# Verify quantity left // sale orders
		if orderline.item.quantity != None:
			if orderline.item.quantity < quantityBySale.get(orderline.item.pk, 0) + orderline.quantity:
				errors.append("Vous avez déjà pris {} {} sur un total de {} par personne." \
					.format(quantityBySale.get(orderline.item.pk, 0), orderline.item.name, orderline.item.max_per_user))

		# Verif cotisant
		if orderline.item.usertype.name == UserType.COTISANT:
			if user.usertype.name != UserType.COTISANT:
				errors.append("Vous devez être {} pour prendre {}.".format(UserType.COTISANT, orderline.item.name))

		# Verif non cotisant (ultra sale mais flemme)
		if orderline.item.usertype.name == UserType.NON_COTISANT:
			if user.usertype.name == UserType.EXTERIEUR:
				errors.append("Vous devez être {} pour prendre {}.".format("UTCéen", orderline.item.name))

	return errors



def changeOrderStatus(order, transaction):
	if transaction['status'] == 'A':
		order.status = OrderStatus.EXPIRED.value
		order.save()
		resp = {
			'status': OrderStatus.EXPIRED.name,
			'message': 'Votre commande a expiré.'
		}
	elif transaction['status'] == 'V':
		if order.status == OrderStatus.NOT_PAYED.value:
			createOrderLineItemsAndFields(order)
		order.status = OrderStatus.PAYED.value
		# order.save()	# TODO DEBUG
		resp = {
			'status': OrderStatus.PAYED.name,
			'message': 'Votre commande a été payée.'
		}
	else:
		resp = {
			'status': OrderStatus.NOT_PAYED.name,
			'url': PAYUTC_TRANSACTION_BASE_URL + str(transaction['id'])
		}
	return JsonResponse(resp, status=status.HTTP_200_OK)


# OrderLine
def getFieldDefaultValue(default, order):
	if default is None:
		return None
	return {
		'owner.first_name': order.owner.first_name,
		'owner.last_name': order.owner.last_name,
	}[default]

def createOrderLineItemsAndFields(order):
	# Create OrderLineItems
	for orderline in order.orderlines.all():
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



def errorResponse(message, errors, httpStatus):
	resp = {
		'message': message,
		'errors': [ {'detail': e} for e in errors ]
	}
	return JsonResponse(resp, status=httpStatus)

def orderErrorResponse(errors):
	return errorResponse('Erreur lors de la vérification de la commande.', errors, status.HTTP_400_BAD_REQUEST)
