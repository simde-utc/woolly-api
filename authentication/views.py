from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from core.viewsets import ModelViewSet

from rest_framework.permissions import AllowAny
from .permissions import *

from .serializers import UserSerializer, UserTypeSerializer
from .models import UserType, User
from .oauth import OAuthAPI, OAuthError


class UserViewSet(ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = (IsUserOrAdmin,)

	def get_queryset(self):
		user = self.request.user
		queryset = self.queryset

		# Anonymous users see nothing
		# if not user.is_authenticated:
		# 	return None

		# if 'user_pk' in self.kwargs:
		# 	association_pk = self.kwargs['user_pk']
		# 	queryset = queryset.filter(user__pk=association_pk)

		return queryset

	# Block create and redirect to login
	def create(self, request, *args, **kwargs):
		return redirect('login')

	# TODO : block self is_admin -> True
	# def update(self, request, *args, **kwargs):
		# pass


class UserTypeViewSet(ModelViewSet):
	queryset = UserType.objects.all()
	serializer_class = UserTypeSerializer
	permission_classes = (IsAdminOrReadOnly,)

	def get_queryset(self):
		queryset = self.queryset

		# user-usertype-list route
		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(users__pk=user_pk)  # TODO Not working

		return queryset


# ========================================================
# 		Auth Management
# ========================================================

class AuthView:
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
		try:
			resp = cls.oauth.callback_and_create_session(request)
			return redirect(resp)
		except OAuthError as error:
			return Response({
				'error': 'OAuthError',
				'message': str(error)
			}, status=status.HTTP_400_BAD_REQUEST)

	@classmethod
	def me(cls, request):
		"""
		Get information about the authenticated user
		"""
		me = request.user
		if me.is_anonymous:
			user = None
		else:
			include_query = request.GET.get('include')
			include_map = ModelViewSet.get_include_map(include_query)
			user = UserSerializer(me, context={ 'include_map': include_map}).data
		return Response({
			'authenticated': me.is_authenticated,
			'user': user
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
