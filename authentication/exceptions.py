from rest_framework import status

from core.exceptions import APIException


class OAuthException(APIException):
    """
    Custom OAuth Error for better feedback
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Une erreur est survenue avec l'authentification, veuillez contactez un administrateur"
    default_code = 'oauth_error'

    @classmethod
    def from_response(cls, response, code: str=None) -> 'OAuthException':
        """
        Create a OAuthException from an OAuth response
        """
        message = response.json().get('message', 'Unknown error')
        details = None

        if 'unauthenticated' in message.lower():
            details = message
            code = code or 'unauthenticated'
            message = "Requête OAuth non authentifié"  # TODO Better message

        return cls(message, code, details)