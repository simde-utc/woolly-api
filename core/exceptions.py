from typing import Any
import logging

from rest_framework import exceptions, status

logger = logging.getLogger(f"woolly.{__name__}")


class APIException(exceptions.APIException):
    """
    Custom APIException for better uniformity

    Attributes:
        message:        the error message explaining the error
        code:           the short string code error
        details:        possible serializabled details
        status_code:    the status code of the response
        default_detail: the default error message
        default_code:   the default error code
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Une erreur interne est survenue, veuillez contactez un administrateur"
    default_code = 'internal_error'

    def __init__(self, message: str=None, code: str=None, details: Any=None, status_code: int=None):
        super().__init__(message, code)
        self.message = str(self.detail)
        self.code = self.detail.code
        self.details = details
        if status_code is not None:
            self.status_code = status_code

    def get_full_details(self) -> dict:
        """
        Return the full detailed error for the response
        """
        return {
            'error': type(self).__name__,
            'message': self.message,
            'code': self.code,
            'details': self.details,
        }

    def __repr__(self) -> str:
        return f"<{type(self).__name__} [{self.code}]>"


class InvalidRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Votre requête n'est pas valide"
    default_code = 'invalid_request'


def exception_handler(error: Exception, context: dict):
    """
    Custom exception handler for more detailled errors
    """
    from rest_framework.views import exception_handler as base_exception_handler
    response = base_exception_handler(error, context)

    # Unhandled error
    if response is None:
        logger.critical("Unhandled error", error, exc_info=True)
        return None

    # Handled error
    if isinstance(error, APIException):
        response.data = error.get_full_details()

    return response
