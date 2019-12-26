from rest_framework import exceptions
from typing import Sequence

# exceptions.ValidationError
# TODO Commit later

class APIException(exceptions.APIException):
	# status_code = 503
	# default_detail = 'Service temporarily unavailable, try again later.'
	# default_code = 'service_unavailable'

	# TODO Improve APIException
	# https://www.django-rest-framework.org/api-guide/exceptions/
	pass

# TODO move
class TransactionException(Exception):
	def __init__(self, message: str, detail: Sequence[str]=[]):
		super().__init__(message)
		self.detail = detail
