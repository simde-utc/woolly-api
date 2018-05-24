from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework_json_api.views import RelationshipView

from rest_framework.permissions import IsAuthenticated
from .serializers import WoollyUserSerializer, WoollyUserTypeSerializer
from .models import WoollyUserType, WoollyUser

from .services import OAuthAPI, JWTClient
# from sales.models import AssociationMember


class WoollyUserViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows Users to be viewed or edited.
	support Post request to create a new WoollyUser
	"""
	queryset = WoollyUser.objects.all()
	serializer_class = WoollyUserSerializer
	# permission_classes = (IsAuthenticated,)

	# def perform_create(self, serializer):
		# serializer.save(type_id = self.kwargs['woollyusertype_pk'])
		# serializer.save()

		# def get_queryset(self):
	# 	queryset = self.queryset.filter(login=self.request.user.login)
	# 	if 'woollyuser_pk' in self.kwargs:
	# 		association_pk = self.kwargs['woollyuser_pk']
	# 		queryset = queryset.filter(user__pk=association_pk)
	# 	return queryset

class WoollyUserTypeViewSet(viewsets.ModelViewSet):
	queryset = WoollyUserType.objects.all()
	serializer_class = WoollyUserTypeSerializer
	permission_classes = (IsAuthenticated,)

	# TODO : Normal que cela ne retourne que l'usertype loggué ?
	# def get_queryset(self):
	# 	queryset = self.queryset.filter(users=self.request.user)

	# 	if 'itemspec_pk' in self.kwargs:
	# 		itemspec_pk = self.kwargs['itemspec_pk']
	# 		queryset = WoollyUserType.objects.all().filter(itemspecifications__pk=itemspec_pk)

	# 	if 'user_pk' in self.kwargs:
	# 		user_pk = self.kwargs['user_pk']
	# 		queryset = WoollyUserType.objects.all().filter(users__pk=user_pk)

	# 	return queryset


class WoollyUserRelationshipView(RelationshipView):
	queryset = WoollyUser.objects


# ========================================================
# 		Auth & JWT Management
# ========================================================

def get_jwt_from_request(request):
	"""
	Helper to get JWT from request
	Return None if no JWT
	"""
	try:
		jwt = request.META['HTTP_AUTHORIZATION']	# Traité automatiquement par Django
	except KeyError:
		return None
	if not jwt or jwt == '':
		return None
	return jwt[7:]		# substring : Bearer ...


class AuthView:
	oauth = OAuthAPI()
	jwtClient = JWTClient()

	@classmethod
	def login(cls, request):
		"""
		Redirect to OAuth api authorization url with an added front callback
		"""
		redirection = request.GET.get('redirect', '')
		url = cls.oauth.get_auth_url(redirection)
		# print(url)
		# return JsonResponse({ 'url': url}) 			# DEBUG
		return redirect(url)

	@classmethod
	def login_callback(cls, request):
		"""
		# Get user from API, find or create it in Woolly, store the OAuth token, create and return a user JWT or an error
		Get user from API, find or create it in Woolly, store the OAuth token, create and redirect to the front with a code to get a JWT
		"""
		after = request.GET.get('after', '')
		resp = cls.oauth.callback_and_create_session(request.GET.get('code', ''), request.GET.get('state', ''));
		# !! Can return dict errors
		# return JsonResponse({ 'redirect': resp })		# DEBUG
		return redirect(resp)

	@classmethod
	def me(cls, request):
		me = request.user
		return JsonResponse({
			'authenticated': me.is_authenticated,
			'user': None if me.is_anonymous else WoollyUserSerializer(me).data
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
