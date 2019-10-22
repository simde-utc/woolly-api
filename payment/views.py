from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.helpers import ErrorResponse, get_field_default_value
from core.exceptions import TransactionException
from rest_framework import status
from django.urls import reverse

from sales.permissions import IsOrderOwnerOrAdmin
from sales.models import *
from .helpers import OrderValidator

from woolly_api.settings import PAYUTC_KEY
from authentication.oauth import OAuthAuthentication
from .services.payutc import Payutc


class PaymentView:
	payutc = Payutc({ 'app_key': PAYUTC_KEY })

	@classmethod
	@permission_classes([IsOrderOwnerOrAdmin])
	def pay(cls, request, pk):
		"""
		Pay an order

		Steps:
			1. Retrieve Order
			2. Verify Order
			3. Create Transaction
			4. Save Transaction info and redirect
		"""
		# 1. Retrieve Order
		try:
			# TODO ajout de la limite de temps
			order = Order.objects.filter(owner__pk=request.user.pk) \
			             .filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
			             .select_related('sale', 'owner') \
			             .get(pk=pk)
		except Order.DoesNotExist as error:
			return ErrorResponse(error, status=status.HTTP_404_NOT_FOUND)

		# 2. Verify Order
		try:
			validator = OrderValidator(order, raise_on_error=True)
			validator.validate()
		except OrderValidationException as error:
			return ErrorResponse(error)

		# 3. Create Transaction
		try:
			return_url = request.GET['return_url']
			callback_url = cls.get_callback_url(request, order)
			transaction = cls.payutc.create_transaction(order, callback_url, return_url)
		except TransactionException as error:
			return ErrorResponse(error)

		# 4. Save transaction id and redirect
		order.status = OrderStatus.AWAITING_PAYMENT.value
		order.tra_id = transaction['tra_id']
		order.save()

		# Redirect to transaction url
		resp = {
			'status': order.get_status_display(),
			'redirect_url': transaction['url'],
		}
		return Response(resp, status=status.HTTP_200_OK)

	@classmethod
	def callback(cls, request, pk):
		"""
		Callback after the transaction has been made
		to validate, cancel or redirect the order
		"""
		try:
			order = Order.objects.select_related('sale__association').get(pk=pk)
		except Order.DoesNotExist as error:
			return ErrorResponse(error, status=status.HTTP_404_NOT_FOUND)

		# Get transaction status
		try:
			transaction_status = cls.payutc.get_transaction_status(order)
		except TransactionException as error:
			return ErrorResponse(error)

		# Update order
		resp = order.update_status(transaction_status)

		if resp.pop('redirect_to_payment', False):
			resp['redirect_url'] = cls.payutc.get_redirection_to_payment(order)

		return Response(resp, status=status.HTTP_200_OK)

	@classmethod
	def get_callback_url(cls, request, order) -> str:
		"""
		Build the url callback for an order
		"""
		return request.build_absolute_uri(
			reverse('pay-callback', kwargs={ 'pk': order.pk })
		)

# Set all endpoint method from PaymentView as API View
for key in ('pay', 'callback'):
	setattr(PaymentView, key, api_view(['GET'])(getattr(PaymentView, key)))

