from core.exceptions import TransactionException
from sales.models import OrderStatus
from typing import Sequence
import requests
import json

PAYUTC_TRANSACTION_BASE_URL = 'https://payutc.nemopay.net/validation?tra_id='

PAYUTC_TO_ORDER_STATUS = {
	'A': OrderStatus.EXPIRED,
	'V': OrderStatus.PAID,
	'W': OrderStatus.AWAITING_PAYMENT,
}

class PayutcException(TransactionException):

	@classmethod
	def from_response(cls, resp: dict):
		"""
		Create an exception from an API response
		"""
		if 'error' not in resp:
			return cls("Erreur inconnue")

		# Build error
		error = resp['error']
		message = error.get('message', "Erreur inconnue")
		detail = [ f"{k}: {m}" for k, m in error.get('data', {}).items() ]
		return cls(message, detail)

class Payutc:

	def __init__(self, params: dict):
		if 'app_key' not in params:
			raise PayutcException("Payutc service need an app_key")

		self.config = {
			'url': 'https://api.nemopay.net',
			'username': None,
			'password': None,
			'systemID': 'payutc',
			'app_key': params['app_key'],
			'fun_id': params.get('fun_id', None),
			'sessionID': None,
			'logged_usr': None,
			'loginMethod': 'payuser',
		}

	def _filter_params(self, params: dict, keys: Sequence[str]) -> dict:
		"""
		Filter params to only return keys
		"""
		data = { k: params.get(k, None) for k in keys }
		# Default values
		if 'fun_id' in keys and data['fun_id'] is None:
			data['fun_id'] = self.config['fun_id']
		return data

	def _call(self, service: str, method: str, data: dict) -> dict:
		"""
		Generic API Call
		"""
		url = f"{self.config['url']}/services/{service}/{method}" \
		    + f"?system_id={self.config['systemID']}&app_key={self.config['app_key']}"
		if self.config['sessionID'] is not None:
				url += f"&sessionid={self.config['sessionID']}"

		response = requests.post(url, json=data, headers={ 'Content-Type': 'application/json' })
		return json.loads(response.text)

	def _create_transaction(self, params: dict) -> dict:
		"""
		API call to create a transaction
		"""
		keys = ('items', 'mail', 'return_url', 'fun_id', 'callback_url')
		data = self._filter_params(params, keys)
		data['fun_id'] = str(data['fun_id'])
		return self._call("WEBSALE", "createTransaction", data)

	def _get_transaction(self, params: dict) -> dict:
		"""
		API call to create a transaction
		"""
		data = self._filter_params(params, ('tra_id', 'fun_id'))
		return self._call("WEBSALE", "getTransactionInfo", data)

	# ============================================
	# 	Transactions
	# ============================================

	def create_transaction(self, order: 'Order', callback_url: str, return_url: str, **kwargs) -> dict:
		"""
		Adapter to create transaction from an order
		"""
		orderlines = order.orderlines.filter(quantity__gt=0).prefetch_related('item')
		itemsArray = [ [int(orderline.item.nemopay_id), orderline.quantity] for orderline in orderlines ]

		resp = self._create_transaction({
			'fun_id': int(order.sale.association.fun_id),
			'items': str(itemsArray),
			'mail': order.owner.email,
			'callback_url': callback_url,
			'return_url': return_url,
		})

		if 'error' in resp:
			raise PayutcException.from_response(resp)

		return resp

	def get_transaction_status(self, order: 'Order') -> dict:
		"""
		Adapter to get transaction status from an order
		"""
		trans = self._get_transaction({
			'tra_id': int(order.tra_id),
			'fun_id': int(order.sale.association.fun_id),
		})

		try:
			return PAYUTC_TO_ORDER_STATUS.get(trans['status'], None)
		except KeyError as error:
			raise TransactionException("Le statut de la transaction est inconnue",
			                           [f"Status: {trans['status']}"])

	def get_redirection_to_payment(self, order: 'Order') -> str:
		"""
		Get the redirection url to the order payment
		"""
		if not order.tra_id:
			raise PayutcException("Order has not transaction id registered")
		return PAYUTC_TRANSACTION_BASE_URL + str(order.tra_id)
