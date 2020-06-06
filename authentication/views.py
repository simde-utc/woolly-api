from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.permissions import IsAdminOrReadOnly
from core.viewsets import ModelViewSet, APIModelViewSet
from authentication.oauth import OAuthAPI
from authentication.models import UserType, User
from authentication.permissions import IsUserOrAdmin
from authentication.serializers import UserSerializer, UserTypeSerializer


class UserViewSet(APIModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrAdmin,)


class UserTypeViewSet(ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


# ========================================================
#       Auth Management
# ========================================================

class AuthView:
    """
    Authentication view

    Login, logout and get information of the current user
    """
    oauth = OAuthAPI()

    @classmethod
    def login(cls, request):
        """
        Redirect to OAuth api authorization url with an added front callback
        """
        redirection = request.GET.get('redirect', 'root')
        url = cls.oauth.get_auth_url(redirection)
        return redirect(url)

    @classmethod
    def login_callback(cls, request):
        """
        Get user from API, find or create it in Woolly, store the OAuth token,
        and redirect to the front with a session
        """
        resp = cls.oauth.callback_and_create_session(request)
        return redirect(resp)

    @classmethod
    def me(cls, request):
        """
        Get information about the authenticated user
        """
        me = request.user
        if me.is_anonymous:
            user = None
        else:
            include_tree = ModelViewSet.get_include_tree(request.GET)
            user = UserSerializer(me, context={ 'include_tree': include_tree }).data
        return Response({
            'authenticated': me.is_authenticated,
            'user': user,
        })

    @classmethod
    def logout(cls, request):
        """
        Delete session and redirection to logout
        """
        redirection = request.GET.get('redirect', None)
        url = cls.oauth.logout(request, redirection)
        return redirect(url)


# Set all method from AuthView as API View
for key in ('login', 'login_callback', 'me', 'logout'):
    setattr(AuthView, key, api_view(['GET'])(getattr(AuthView, key)))
