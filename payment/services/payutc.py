import logging
from math import ceil

from django.conf import settings
from rest_framework import status

from sales.models import Sale, Order, OrderStatus, Item
from .base import AbstractPaymentService, TransactionException
from .payutc_client import PayutcClient, PayutcException as PayutcClientException


logger = logging.getLogger(f"woolly.{__name__}")

PAYUTC_TO_ORDER_STATUS = {
    'A': OrderStatus.EXPIRED,
    'V': OrderStatus.PAID,
    'W': OrderStatus.AWAITING_PAYMENT,
}


class PayutcException(TransactionException):
    """
    PayUTC service specific exception
    """
    pass


class PayutcService(AbstractPaymentService):

    def __init__(self):
        super().__init__()
        self.client = PayutcClient(settings.PAYUTC)

    def _check_login(self) -> None:
        """Check that the client is logged to the app"""
        if not self.client.is_authenticated:
            self.client.login_app()
            self.client.login_user()
            logger.debug("Logged in Payutc services")

    def _get_category_id(self, sale: Sale) -> int:
        data = {
            "name": f"Woolly - {sale.id}",
            "fundation": sale.association.fun_id,
        }
        try:
            try:
                return self.client.get_categories(data)[0]["id"]
            except IndexError:
                logger.info(f"Creating category {data['name']} on fundation {data['fundation']}")
                data["fun_id"] = data.pop("fundation")
                return self.client.upsert_category(data)
        except PayutcClientException as error:
            message = "Erreur lors de la mise à jour la catégorie"
            raise PayutcException(message, code="category_creation_error") from error

    def sync_item(self, item: Item, **kwargs) -> None:
        """
        Adapter to synchronize an item in the payment service
        """
        self._check_login()
        sale = item.sale
        data = {
            "name": item.name,
            "prix": ceil(item.price * 100),
            "tva": 5.5,
            "parent": self._get_category_id(sale),
            "cotisant": item.usertype == "cotisant_bde",
            "fun_id": sale.association.fun_id,
        }

        action = "Updating" if item.pk else "Creating"
        logger.info(f"{action} item {data['name']} on fundation {data['fun_id']}")
        try:
            item.nemopay_id = self.client.upsert_product(data, id=item.nemopay_id)
        except PayutcClientException as error:
            message = "Erreur lors de la mise à jour l'article"
            raise PayutcException(message, code="item_synch_error") from error

    def create_transaction(self, order: Order, callback_url: str, return_url: str, **kwargs) -> dict:
        """
        Adapter to create transaction from an order
        """
        orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item')
        itemsArray = [ [int(orderline.item.nemopay_id), orderline.quantity] for orderline in orderlines ]

        try:
            return self.client.create_transaction({
                'fun_id': int(order.sale.association.fun_id),
                'items': str(itemsArray),
                'mail': order.owner.email,
                'callback_url': callback_url,
                'return_url': return_url,
            })
        except PayutcClientException as error:
            message = "Erreur lors de la création de la transaction"
            raise PayutcException(message, code="transaction_creation_error") from error

    def get_transaction_status(self, order: Order) -> OrderStatus:
        """
        Adapter to get transaction status from an order
        """
        try:
            trans = self.client.get_transaction({
                'tra_id': int(order.tra_id),
                'fun_id': int(order.sale.association.fun_id),
            })
        except PayutcClientException as error:
            message = "Erreur lors de la récupération de la transaction"
            raise PayutcException(message, code="transaction_fetch_error") from error

        try:
            return PAYUTC_TO_ORDER_STATUS.get(trans['status'], None)
        except KeyError as error:
            raise PayutcException(
                "Le statut de la transaction est inconnue",
                "unknown_transaction_status",
                details=f"Status: {trans.get('status')}") from error

    def get_redirection_to_payment(self, order: Order, callback_url: str, return_url: str) -> str:
        """
        Get the redirection url to the order payment
        """
        if not order.tra_id:
            raise PayutcException(
                "La commande n'a pas de transaction enregistrée",
                'order_has_no_transaction',
                status_code=status.HTTP_400_BAD_REQUEST)

        return self.client.get_payment_url(order.tra_id)
