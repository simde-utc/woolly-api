from django.conf import settings

from payment.services.base import AbstractPaymentService
from payment.services.payutc import PayutcService
# from sales.models import Order


def get_pay_service(*args, **kwargs) -> AbstractPaymentService:
    """
    Instanciate the requested payment service
    """
    # TODO Select pay service
    # if request is not None:
    #     pay_service = request.data.get('pay_service')
    if settings.STAGE == "test":
        from payment.services.fake import FakePaymentService
        return FakePaymentService()
    else:
        return PayutcService()
