from django.http import JsonResponse
from django.shortcuts import redirect
from core.viewsets import ModelViewSet

from rest_framework.permissions import AllowAny
from .permissions import *

from .serializers import UserSerializer, UserTypeSerializer
from .models import UserType, User
from .oauth import OAuthAPI


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
		# TODO Raise and catch error
		if 'error' in resp:
			return JsonResponse(resp)
		return redirect(resp)

	@classmethod
	def me(cls, request):
		cls.oauth.authenticate(request)
		me = request.user
		if me.is_anonymous:
			user = None
		else:
			include_query = request.GET.get('include')
			include_map = ModelViewSet.get_include_map(include_query)
			user = UserSerializer(me, context={ 'include_map': include_map}).data
		return JsonResponse({
			'authenticated': me.is_authenticated,
			'user': user
		})

	@classmethod
	def logout(cls, request):
		redirection = request.GET.get('redirect', None)
		url = cls.oauth.logout(request, redirection)
		return redirect(url)
