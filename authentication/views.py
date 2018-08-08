from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework_json_api import views
from authlib.specs.rfc7519 import JWTError

from rest_framework.permissions import AllowAny
from .permissions import *

from .serializers import UserSerializer, UserTypeSerializer
from .models import UserType, User
from .services import OAuthAPI, JWTClient, get_jwt_from_request


class UserViewSet(views.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	permission_classes = (IsUserOrAdmin,)

	# Block create and redirect to login
	def create(self, request, *args, **kwargs):
		return redirect('auth.login')

	# TODO : block self is_admin -> True
	def update(self, request, *args, **kwargs):
		pass

	def get_queryset(self):
		user = self.request.user
		queryset = self.queryset

		# Anonymous users see nothing
		if not user.is_authenticated:
			return None

		# if 'user_pk' in self.kwargs:
		# 	association_pk = self.kwargs['user_pk']
		# 	queryset = queryset.filter(user__pk=association_pk)

		return queryset

class UserTypeViewSet(views.ModelViewSet):
	queryset = UserType.objects.all()
	serializer_class = UserTypeSerializer
	permission_classes = (AllowAny,)

	def get_queryset(self):
		# Visible by everyone by default
		queryset = self.queryset

		if 'itemspec_pk' in self.kwargs:
			itemspec_pk = self.kwargs['itemspec_pk']
			queryset = UserType.objects.all().filter(itemspecifications__pk=itemspec_pk)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = UserType.objects.all().filter(users__pk=user_pk)

		return queryset


class UserRelationshipView(views.RelationshipView):
	queryset = User.objects


# ========================================================
# 		Auth & JWT Management
# ========================================================

class AuthView:
	oauth = OAuthAPI()
	jwtClient = JWTClient()

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
		create and return a user JWT or an error
		Get user from API, find or create it in Woolly, store the OAuth token, 
		create and redirect to the front with a code to get a JWT
		"""
		resp = cls.oauth.callback_and_create_session(request);
		print(resp)
		# !! Can return dict errors
		if 'error' in resp:
			return JsonResponse(resp)
		return redirect(resp)

	@classmethod
	def me(cls, request):
		me = request.user
		return JsonResponse({
			'authenticated': me.is_authenticated,
			'user': None if me.is_anonymous else UserSerializer(me).data
		})

	@classmethod
	def logout(cls, request):
		jwt = get_jwt_from_request(request)
		logout_url = cls.oauth.logout(jwt)
		return JsonResponse({
			'logout': True,
			'logout_url': logout_url
		})


class JWTView:
	jwtClient = JWTClient()

	@classmethod
	def get_jwt(cls, request):
		"""
		Get first JWT after login from random session code
		"""
		code = request.GET.get('code', '')
		return JsonResponse(cls.jwtClient.get_jwt_after_login(code))

	# TODO NOT FINISHED : revoke
	@classmethod
	def refresh_jwt(cls, request):
		jwt = get_jwt_from_request(request)
		return JsonResponse(cls.jwtClient.refresh_jwt(jwt))

	@classmethod
	def validate_jwt(cls, request):
		jwt = get_jwt_from_request(request)
		try:
			cls.jwtClient.validate(jwt)
			valid = True
		except JWTError as error:
			valid = False
		return JsonResponse({ 'valid': valid })
