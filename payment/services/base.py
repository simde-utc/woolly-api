from abc import ABC, abstractmethod
from sales.models import Order, OrderStatus


class TransactionException(Exception):
	"""
	Exception that is raised during payment transactions
	"""

	def __init__(self, message, detail=None):
		super().__init__(message)
		self.detail = detail

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
