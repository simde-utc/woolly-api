from abc import ABC, abstractmethod

from rest_framework import status

from core.exceptions import APIException
from sales.models import Order, OrderStatus


class TransactionException(APIException):
    """
    Exception that is raised during payment transactions
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Une erreur est survenue au cours de la transaction, veuillez contactez un administrateur"
    default_code = 'unknown_transaction_error'


class AbstractPaymentService(ABC):
    """
    Base abstract class for payment services
    """

    @abstractmethod
    def create_transaction(self, order: Order, callback_url: str, return_url: str, **kwargs) -> dict:
        """
        Adapter to create transaction from an order
        """
        pass

    @abstractmethod
    def get_transaction_status(self, order: Order) -> OrderStatus:
        """
        Adapter to get transaction status from an order
        """
        pass

    @abstractmethod
    def get_redirection_to_payment(self, order: Order) -> str:
        """
        Get the redirection url to the order payment
        """
        pass
