from typing import Union

from authlib.common.errors import AuthlibBaseError
from authlib.integrations.requests_client import OAuth2Session
from django.core.cache import cache
from django.contrib import auth as django_auth
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed

from woolly_api.settings import OAUTH as OAuthConfig
from core.helpers import filter_dict_keys
from authentication.exceptions import OAuthException, OAuthTokenException

OAUTH_TOKEN_NAME = 'oauth_token'

UserModel = django_auth.get_user_model()
UserOrNone = Union[UserModel, None]


def get_user_from_request(request) -> UserOrNone:
    """
    Get the user from the request session
    Can debug logged user like this:
    > return UserModel(email='test@woolly.com')
    """
    # Try to get the user logged in the request
    user = getattr(request, '_request', request).user
    if user.is_authenticated:
        if user.fetched_data:
            return user

        # Add api data and return user
        try:
            oauth_client = OAuthAPI(session=request.session)
            return user.get_with_api_data(oauth_client)
        except OAuthTokenException:
            # Flush session
            oauth_client.logout(request)
            return None

    # Get the user from the session
    user_id = request.session.get('user_id')
    if not user_id:
        return None

    try:
        oauth_client = OAuthAPI(session=request.session)
        return UserModel.objects.get_with_api_data(oauth_client, pk=user_id)
    except UserModel.DoesNotExist:
        raise AuthenticationFailed("user_id does not match a user")
    except OAuthTokenException:
        # Flush session
        oauth_client.logout(request)
        return None


class OAuthAPI:
    """
    Accès à l'API du portail des assos ou autre API OAuth2
    Utile pour la connexion, la récupération des droits
    """

    def __init__(self, provider: str='portal', config: dict=None, token: dict=None, session=None):
        """
        OAuth2 Client initialisation
        """
        self.provider = provider
        self.config = config or OAuthConfig[provider].copy()
        if token:
            self.config['token'] = token
        elif session:
            self.config['token'] = session.get(OAUTH_TOKEN_NAME)
        self.client = OAuth2Session(**self.config)

    def get_auth_url(self, redirection: str) -> str:
        """
        Return authorization url
        """
        # Get url and state from OAuth server
        url, state = self.client.create_authorization_url(self.config['authorize_url'])

        # Cache front url with state for 5mins
        cache.set(state, redirection, 300)
        return url

    def callback_and_create_session(self, request) -> str:
        """
        Get token, user informations, store these and redirect
        """
        # Get code and state from request
        # TODO Checks
        code = request.GET['code']
        state = request.GET['state']

        # Get token from code
        try:
            token = self.client.fetch_access_token(self.config['access_token_url'], code=code)
        except AuthlibBaseError as error:
            raise OAuthException(
                "Impossible de récuperer le Token OAuth",
                "fetch_access_token_error",
                details=str(error)
            ) from error

        # Fetch and login user into Django, then create session
        user = self.fetch_user()
        request.user = user
        django_auth.login(request, user)
        request.session['user_id'] = str(user.id)
        request.session[OAUTH_TOKEN_NAME] = token

        # Get front redirection from cached state
        redirection = cache.get(state)
        cache.delete(state)
        return redirection or 'root'

    def logout(self, request, redirection: str=None) -> str:
        """
        Logout the user from Woolly and redirect to the provider's logout
        """
        # Revoke user token ??? POSSIBLE TODO
        # token = request.session.get(OAUTH_TOKEN_NAME)
        # if token:
        #   self.client.revoke_token(url, token)

        # Logout from Django
        request.user = None
        django_auth.logout(request)

        # Redirect to logout
        return self.config['logout_url']

    def fetch_resource(self, query: str) -> Union[dict, list]:
        """
        Return data from the API if valid else raise an OAuthException
        """
        try:
            resp = self.client.get(self.config['base_url'] + query)
        except AuthlibBaseError as error:
            code = getattr(error, 'error', None)
            raise OAuthTokenException(code=code) from error

        if resp.status_code == 200:
            return resp.json()

        raise OAuthException.from_response(resp)

    def fetch_user(self, user_id: str=None) -> UserModel:
        """
        Get specified or current user
        """
        # Get and patch data from API
        url = (f"users/{user_id}" if user_id else "user") + "/?types=*"
        data = self.fetch_resource(url)
        if hasattr(UserModel, 'patch_fetched_data'):
            data = UserModel.patch_fetched_data(data)

        # Get or create user from db
        new_user = False
        try:
            user = UserModel.objects.get(pk=data['id'])
        except UserModel.DoesNotExist:
            fields_data = filter_dict_keys(data, UserModel.field_names())
            user = UserModel(**fields_data)
            new_user = True

        # Update with fetched data and return
        updated_fields = user.sync_data(data, save=False)
        if updated_fields or new_user:
            user.save()

        return user


class OAuthBackend(ModelBackend):
    """
    django.contrib.auth custom Backend with OAuth
    """

    def authenticate(self, request, **kwargs) -> UserOrNone:
        """
        For django authentication
        """
        return get_user_from_request(request)

    def get_user(self, user_id: str) -> UserOrNone:
        # Try to get full user from cache
        cached_user = UserModel.get_from_cache({ 'pk': user_id }, single_result=True)
        if cached_user is not None:
            return cached_user

        # Return simple user as a fallback
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class OAuthAuthentication(SessionAuthentication):
    """
    rest_framework custom Authentication with OAuth
    """

    def authenticate(self, request, **kwargs):
        """
        For rest_framework authentication
        """
        user = get_user_from_request(request)
        if user:
            self.enforce_csrf(request)
            return (user, None)
        else:
            return None
