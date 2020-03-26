from rest_framework import status

from core.exceptions import APIException


class OrderValidationException(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = "La commande n'est pas valide"
    default_code = 'invalid_order'
