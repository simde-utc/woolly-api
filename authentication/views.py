from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework_json_api import views

from rest_framework.permissions import AllowAny
from .permissions import *

from .auth import APIAuthentication
from .serializers import UserSerializer, UserTypeSerializer
from .models import UserType, User
from .services import OAuthAPI


class UserViewSet(views.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = (IsUserOrAdmin,)

	# Block create and redirect to login
	def create(self, request, *args, **kwargs):
		return redirect('auth.login')

	# TODO : block self is_admin -> True
	# def update(self, request, *args, **kwargs):
		# pass

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


class UserRelationshipView(views.RelationshipView):
	queryset = User.objects


class UserTypeViewSet(views.ModelViewSet):
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


class UserTypeRelationshipView(views.RelationshipView):
	queryset = UserType.objects


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
		redirection = request.GET.get('redirect', None)
		url = cls.oauth.get_auth_url(redirection)
		return redirect(url)

	@classmethod
	def login_callback(cls, request):
		"""
		# Get user from API, find or create it in Woolly, store the OAuth token,
		create and return a session or an error
		Get user from API, find or create it in Woolly, store the OAuth token,
		and redirect to the front with a session
		"""
		resp = cls.oauth.callback_and_create_session(request)
		# !! Can return dict errors
		if 'error' in resp:
			return JsonResponse(resp)
		return redirect(resp)

	@classmethod
	def me(cls, request):
		APIAuthentication().authenticate(request)
		me = request.user
		return JsonResponse({
			'authenticated': me.is_authenticated,
			'user': None if me.is_anonymous else UserSerializer(me).data
		})

	@classmethod
	def logout(cls, request):
		return JsonResponse({
			'logout': True,
			'logout_url': cls.oauth.logout()
		})
