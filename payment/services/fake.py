from sales.models import Order, OrderStatus, Item
from .base import AbstractPaymentService


class FakePaymentService(AbstractPaymentService):

    def sync_item(self, item: Item, **kwargs) -> None:
        """
        Adapter to synchronize an item in the payment service
        """
        pass

    def create_transaction(self, order: Order, callback_url: str, return_url: str, **kwargs) -> dict:
        """
        Adapter to create transaction from an order
        """
        return {
            'tra_id': 1,
            'url': self.get_redirection_to_payment(order, callback_url, return_url),
        }

    def get_transaction_status(self, order: Order) -> OrderStatus:
        """
        Adapter to get transaction status from an order
        """
        return OrderStatus.PAID

    def get_redirection_to_payment(self, order: Order, callback_url: str, return_url: str) -> str:
        """
        Get the redirection url to the order payment
        """
        return return_url
