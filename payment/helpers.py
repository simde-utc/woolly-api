from woolly_api.settings import PAYUTC_KEY, TEST_MODE
from payment.services.base import AbstractPaymentService
from payment.services.payutc import Payutc
from sales.models import Order

def get_pay_service(order: Order, request=None) -> AbstractPaymentService:
	"""
	Instanciate the requested payment service
	"""
	if request is not None:
		pay_service = request.data.get('pay_service')
	if TEST_MODE:
		from payment.services.fake import FakePaymentService
		return FakePaymentService()
	else:
		return Payutc({ 'app_key': PAYUTC_KEY })
