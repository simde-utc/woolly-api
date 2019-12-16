from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.helpers import ErrorResponse, get_field_default_value
from rest_framework import status
from django.urls import reverse
from threading import Lock

from payment.services.base import AbstractPaymentService, TransactionException
from payment.services.payutc import Payutc

from woolly_api.settings import PAYUTC_KEY, TEST_MODE
from authentication.oauth import OAuthAuthentication
from .helpers import OrderValidator, OrderValidationException
from sales.models import Order, OrderStatus


pay_lock = Lock()

class PaymentView:

	@classmethod
	def _get_pay_service(cls, request) -> AbstractPaymentService:
		"""
		Instanciate the requested payment service
		"""
		pay_service = request.data.get('pay_service')
		if TEST_MODE:
			from payment.services.fake import FakePaymentService
			return FakePaymentService()
		else:
			return Payutc({ 'app_key': PAYUTC_KEY })

	@classmethod
	@permission_classes([IsAuthenticated])
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

		# Lock sensitive part
		pay_lock.acquire()

		# 2. Verify Order
		try:
			validator = OrderValidator(order, raise_on_error=True)
			validator.validate()
		except OrderValidationException as error:
			pay_lock.release()
			return ErrorResponse(error)

		# TODO Check if doesn't already have an order

		# 3. Create Transaction
		pay_service = cls._get_pay_service(request)
		try:
			callback_url = request.build_absolute_uri(
				reverse('order-status', kwargs={ 'pk': order.pk })
			)
			return_url = request.GET['return_url']
			transaction = pay_service.create_transaction(order, callback_url, return_url)
		except TransactionException as error:
			pay_lock.release()
			return ErrorResponse(error)

		# 4. Save transaction id and redirect
		try:
			order.status = OrderStatus.AWAITING_PAYMENT.value
			order.tra_id = transaction['tra_id']
			order.save()
		finally:
			pay_lock.release()

		# Redirect to transaction url
		resp = {
			'status': order.get_status_display(),
			'redirect_url': transaction['url'],
		}
		return Response(resp, status=status.HTTP_200_OK)

	@classmethod
	def update_status(cls, request, pk):
		"""
		Callback after the transaction has been made
		to validate, cancel or redirect the order
		"""
		try:
			order = Order.objects.select_related('sale__association').get(pk=pk)
		except Order.DoesNotExist as error:
			return ErrorResponse(error, status=status.HTTP_404_NOT_FOUND)

		# Get transaction status if needed
		if order.status in OrderStatus.AWAITING_LIST.value:
			pay_service = cls._get_pay_service(request)
			try:
				new_status = pay_service.get_transaction_status(order)
			except TransactionException as error:
				return ErrorResponse(error)
		else:
			new_status = None

		# Update order if needed and return the response
		resp = order.update_status(new_status)
		if resp.pop('redirect_to_payment', False):
			resp['redirect_url'] = pay_service.get_redirection_to_payment(order)

		return Response(resp, status=status.HTTP_200_OK)


# Set all endpoint method from PaymentView as API View
for key in ('pay', 'update_status'):
	setattr(PaymentView, key, api_view(['GET'])(getattr(PaymentView, key)))

