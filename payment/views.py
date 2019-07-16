from django.utils import timezone
from functools import reduce

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import *
from django.http import JsonResponse
from django.urls import reverse
from core.helpers import errorResponse
from django.core.mail import EmailMessage

from core.permissions import *
from sales.models import *
from sales.serializers import *
from sales.permissions import *

from woolly_api.settings import PAYUTC_KEY, PAYUTC_TRANSACTION_BASE_URL
from authentication.oauth import OAuthAPI
from .services.payutc import Payutc


# TODO Check if quantities exists first
# orderline.item.group.max_per_user 


# TODO
class PaymentView:
	pass

@api_view(['GET'])
@authentication_classes((OAuthAPI,))
# @permission_classes((IsOwner,))
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
		order = Order.objects.filter(owner=request.user) \
					.filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
					.prefetch_related('sale', 'orderlines', 'owner') \
					.get(pk=pk)
	except Order.DoesNotExist as e:
		return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

	# 2. Verify Order
	errors = verifyOrder(order, request.user)
	if len(errors) > 0:
		return orderErrorResponse(errors)

	# 3. Process orderlines
	orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item').all()
	# Tableau pour Weez
	itemsArray = [ [int(orderline.item.nemopay_id), orderline.quantity] for orderline in orderlines ]
	if reduce(lambda acc, b: acc + b[1], itemsArray, 0) <= 0:
		return orderErrorResponse(["Vous devez avoir un nombre d'items commandé strictement positif."])

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
		'status': 'NOT_PAID',
		'url': transaction['url']
	}
	return JsonResponse(resp, status=status.HTTP_200_OK)


@api_view(['GET'])
def pay_callback(request, pk):
	try:
		order = Order.objects \
					.prefetch_related('sale', 'orderlines', 'owner') \
					.get(pk=pk)
	except Order.DoesNotExist as e:
		return errorResponse(str(e), status=status.HTTP_404_NOT_FOUND)

	payutc = Payutc({ 'app_key': PAYUTC_KEY })
	transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
	if 'error' in transaction:
		print(transaction)
		# TODO parse error
		return errorResponse(transaction['error']['message'])

	return updateOrderStatus(order, transaction)




def verifyOrder(order, user):
	# Error bag to store all error messages
	errors = list()

	# Check if still buyable
	if order.status not in OrderStatus.BUYABLE_STATUS_LIST.value:
		errors.append("Votre commande n'est pas payable.")

	# Check active & date
	if not order.sale.is_active:
		errors.append("La vente n'est pas disponible.")
	now = timezone.now()
	if now < order.sale.begin_at:
		errors.append("La vente n'a pas encore commencé.")
	if now > order.sale.end_at:
		errors.append("La vente est terminée.")
	# TODO
	# print("date")
	# print(now)
	# print(order.sale.begin_at)
	# print(order.sale.end_at)

	# Checkpoint
	if len(errors) > 0:
		return errors

	# Fetch orders made by the user
	userOrders = Order.objects \
					.filter(owner__pk=user.pk, sale__pk=order.sale.pk, status__in=OrderStatus.NOT_CANCELLED_LIST.value) \
					.exclude(pk=order.pk) \
					.prefetch_related('orderlines', 'orderlines__item', 'orderlines__item__group')
	# Count quantity bought by user
	quantityByGroup = dict()
	quantityByUser = dict()
	quantityByUserTotal = 0
	for userOrder in userOrders:
		for orderline in userOrder.orderlines.all():
			# print("orderline.item.group")
			# print(orderline.item.group)
			if orderline.item.group is not None:
				quantityByGroup[orderline.item.group.pk] = orderline.quantity + quantityByGroup.get(orderline.item.group.pk, 0)
			quantityByUser[orderline.item.pk] = orderline.quantity + quantityByUser.get(orderline.item.pk, 0)
			quantityByUserTotal += orderline.quantity
			if userOrder.status in OrderStatus.BUYABLE_STATUS_LIST.value:
				errors.append("Vous avez déjà une commande en cours pour cette vente.")

	# print("quantityByGroup")
	# print(quantityByGroup)

	# Check group max per user
	for orderline in order.orderlines.filter(quantity__gt=0).all():
		if not orderline.item.is_active:
				errors.append("L'item {} n'est pas disponible." \
					.format(orderline.item.name))			
		if orderline.item.group is not None:
			quantityByGroup[orderline.item.group.pk] = quantityByGroup.get(orderline.item.group.pk, 0) + orderline.quantity
			if orderline.item.group.max_per_user is not None and \
				quantityByGroup[orderline.item.group.pk] > orderline.item.group.max_per_user:
				errors.append("Vous ne pouvez pas prendre plus de {} {} par personne." \
					.format(orderline.item.group.max_per_user, orderline.item.group.name))

	# Checkpoint
	if len(errors) > 0:
		return errors


	# Fetch all orders of the sale
	saleOrders = Order.objects \
					.filter(sale__pk=order.sale.pk, status__in=OrderStatus.NOT_CANCELLED_LIST.value) \
					.exclude(pk=order.pk) \
					.prefetch_related('orderlines', 'orderlines__item')
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

		if orderline.item.max_per_user is not None:
			# Verif max_per_user // quantity
			if orderline.quantity > orderline.item.max_per_user:
				errors.append("Vous ne pouvez prendre que {} {} par personne." \
					.format(orderline.item.max_per_user, orderline.item.name))

			# Verif max_per_user // user orders
			if quantityByUser.get(orderline.item.pk, 0) + orderline.quantity > orderline.item.max_per_user:
				errors.append("Vous avez déjà pris {} {} sur un total de {} par personne." \
					.format(quantityByUser.get(orderline.item.pk, 0), orderline.item.name, orderline.item.max_per_user))

		if orderline.item.quantity is not None:
			# Verify quantity left // sale orders
			if orderline.item.quantity < quantityBySale.get(orderline.item.pk, 0) + orderline.quantity:
				errors.append("Il reste moins de {} {}.".format(orderline.quantity, orderline.item.name))

		# Verif cotisant
		if orderline.item.usertype.name == UserType.COTISANT:
			if user.usertype.name != UserType.COTISANT:
				errors.append("Vous devez être {} pour prendre {}.".format(UserType.COTISANT, orderline.item.name))

		# Verif non cotisant (ultra sale mais flemme)
		if orderline.item.usertype.name == UserType.NON_COTISANT:
			if user.usertype.name == UserType.EXTERIEUR:
				errors.append("Vous devez être {} pour prendre {}.".format("UTCéen", orderline.item.name))

	return errors



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


def orderErrorResponse(errors):
	return errorResponse('Erreur lors de la vérification de la commande.', errors, status.HTTP_400_BAD_REQUEST)



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
