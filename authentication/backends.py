from cas.backends import CASBackend
from cas.backends import _verify
from django.contrib.auth import get_user_model
from django.conf import settings
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen
import json
import datetime
from authentication.models import WoollyUserType
from django.contrib.sessions.backends.db import SessionStore
from importlib import import_module

class UpdatedCASBackend(CASBackend):
    """
    An extension of the CASBackend to make it functionnable 
    with custom user models on user creation and selection
    """

    def authenticate(self, ticket, service):
        """
        Verifies CAS ticket and gets or creates User object
        NB: Use of PT to identify proxy
        """
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        print("alaric1")
        UserModel = get_user_model()
        username = _verify(ticket, service)
        print("session 2")
        if not username:
            return None

        try:
            user = UserModel._default_manager.get(**{
                UserModel.USERNAME_FIELD: username
            })
            user = self.configure_user(user)
            user.save()
        except UserModel.DoesNotExist:
            # user will have an "unusable" password
            if settings.CAS_AUTO_CREATE_USER:
                user = UserModel.objects.create_user(username, '')
                user = self.configure_user(user)
                user.save()
            else:
                user = None
        return user

    def configure_user(self, user):
        print("alaric2")
        """
        Configures a user in a custom manner
        :param user: the user to retrieve informations on
        :return: a configured user
        """
        return user


class GingerCASBackend(UpdatedCASBackend):
    """
    A CAS Backend implementing Ginger for User configuration
    """

    def configure_user(self, user):
        print("alaric3")
        """
        Configures a user using Ginger
        :param user: The WoollyUser to configure
        :return: The configurated user
        """
        params = {'key': settings.GINGER_KEY, }
        url = urljoin(settings.GINGER_SERVER_URL, user.login) + \
            '?' + urlencode(params)
        page = urlopen(url)
        response = page.read()
        json_data = json.loads(response.decode())

        user.first_name = json_data.get('prenom').capitalize()
        user.last_name = json_data.get('nom').capitalize()
        user.email = json_data.get('mail')
        if json_data.get('is_adulte'):
            user.birthdate = datetime.date.min
        else:
            user.birthdate = datetime.date.today
        if json_data.get('is_cotisant'):
            user.woollyusertype = WoollyUserType.objects.get(
                name=WoollyUserType.COTISANT)
        else:
            user.woollyusertype = WoollyUserType.objects.get(
                name=WoollyUserType.NON_COTISANT)
        return user
