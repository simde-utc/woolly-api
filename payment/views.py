from threading import Lock

from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from sales.exceptions import OrderValidationException
from sales.models import Order, OrderStatus
from payment.services.base import TransactionException
from payment.validator import OrderValidator
from payment.helpers import get_pay_service


pay_lock = Lock()


class PaymentView:
    """
    View responsible for payment of orders
    """

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
        # TODO ajout de la limite de temps
        order = Order.objects.filter(owner__pk=request.user.pk) \
                     .filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
                     .select_related('sale', 'owner') \
                     .get(pk=pk)

        # Lock sensitive part
        pay_lock.acquire()

        # 2. Verify Order
        try:
            validator = OrderValidator(order, raise_on_error=True)
            validator.validate()
        except OrderValidationException as error:
            pay_lock.release()
            raise error

        # TODO Check if doesn't already have an order

        # 3. Create Transaction
        try:
            pay_service = get_pay_service(order, request)
            callback_url = request.build_absolute_uri(
                reverse('order-status', kwargs={ 'pk': order.pk })
            )
            return_url = request.GET['return_url']
            transaction = pay_service.create_transaction(order, callback_url, return_url)
        except TransactionException as error:
            pay_lock.release()
            raise error

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
        # Update order status
        order = Order.objects.select_related('sale__association').get(pk=pk)
        resp = order.update_status()
        pay_service = get_pay_service(order, request)

        # Return the response
        if resp.pop('redirect_to_payment', False):
            resp['redirect_url'] = pay_service.get_redirection_to_payment(order)

        return Response(resp, status=status.HTTP_200_OK)


# Set all endpoint method from PaymentView as API View
for key in ('pay', 'update_status'):
    setattr(PaymentView, key, api_view(['GET'])(getattr(PaymentView, key)))
