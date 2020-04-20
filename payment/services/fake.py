from sales.models import Order, OrderStatus
from .base import AbstractPaymentService


class FakePaymentService(AbstractPaymentService):

    def create_transaction(self, order: Order, callback_url: str, return_url: str, **kwargs) -> dict:
        """
        Adapter to create transaction from an order
        """
        return {
            'tra_id': 1,
            'url': f"fake_url/{order.id}/?callback={callback_url}&return={return_url}",
        }

    def get_transaction_status(self, order: Order) -> OrderStatus:
        """
        Adapter to get transaction status from an order
        """
        return OrderStatus.PAID

    def get_redirection_to_payment(self, order: Order) -> str:
        """
        Get the redirection url to the order payment
        """
        return f"fake_url/{order.id}"
