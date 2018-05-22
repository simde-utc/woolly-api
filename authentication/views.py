from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework_json_api.views import RelationshipView
from .serializers import WoollyUserSerializer, WoollyUserTypeSerializer
from .models import WoollyUserType, WoollyUser
from .oauth import OAuthAPI, JWTClient
# from sales.models import AssociationMember


class WoollyUserViewSet(viewsets.ModelViewSet):
	"""
	API endpoint that allows Users to be viewed or edited.
	support Post request to create a new WoollyUser
	"""
	queryset = WoollyUser.objects.all()
	serializer_class = WoollyUserSerializer
	permission_classes = (IsAuthenticated,)

	# def perform_create(self, serializer):
		# serializer.save(type_id = self.kwargs['woollyusertype_pk'])
		# serializer.save()

	# TODO : Normal que cela ne retourne que l'user loggué ?
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
# 		Login - Callback - Logout
# ========================================================

def login(request):
	"""
	Redirect to OAuth api authorization url with an added front callback
	"""
	redirection = request.GET.get('redirect', '')
	oauth = OAuthAPI()
	url = oauth.get_auth_url(redirection)
	# print(url)
	# return JsonResponse({ 'url': url}) 			# DEBUG
	return redirect(url)

def login_callback(request):
	"""
	# Get user from API, find or create it in Woolly, store the OAuth token, create and return a user JWT or an error
	Get user from API, find or create it in Woolly, store the OAuth token, create and redirect to the front with a code to get a JWT
	"""
	after = request.GET.get('after', '')
	oauth = OAuthAPI()
	resp = oauth.callback_and_create_session(request.GET.get('code', ''), request.GET.get('state', ''));
	# !! Can return dict errors
	# return JsonResponse({ 'redirect': resp })		# DEBUG
	return redirect(resp)

# TODO Virer
def userInfos(request):
	userId = request.session['_auth_user_id']
	try:
		queryset = WoollyUser.objects.get(id=userId)
		login = queryset.login
		lastName = queryset.last_name
		firstName = queryset.first_name
		# TODO serializer... + permissions
		response = {"userId": userId, "login": login, "lastName": lastName, "firstName": firstName}
	except WoollyUser.DoesNotExist:
		response =  {"userId": None, "login": None, "lastName": None, "firstName": None}
	return JsonResponse(response)

def me(request):
	me = request.user
	print('anonymous' if me.is_anonymous else 'connected')
	return JsonResponse({
		'authenticated': me.is_authenticated,
		'user': None if me.is_anonymous else WoollyUserSerializer(me).data
	})

def logout(request):
	# TODO NOT FINISHED : revoke
	oauth = OAuthAPI()
	return redirect(oauth.logout(get_jwt_from_request(request)))



# ========================================================
# 		JWT Management
# ========================================================

def get_jwt_from_request(request):
	return request.GET.get('jwt', '')

	# TODO OOOOOOOOOOO
def get_jwt(request):
	"""
	Get first JWT after login from random session code
	"""
	code = request.GET.get('code', '')
	oauth = OAuthAPI()
	return JsonResponse(oauth.get_jwt_after_login(code))

# TODO NOT FINISHED : revoke
def refresh_jwt(request):
	jwt = get_jwt_from_request(request)
	jwtClient = JWTClient()
	return JsonResponse(jwtClient.refresh_jwt(jwt))


# TODO a virer
def validate_jwt(request):
	jwt = get_jwt_from_request(request)
	jwtClient = JWTClient()
	return JsonResponse(jwtClient.validate(jwt))
# TODO virer
def test_jwt(request):
	jwt = get_jwt_from_request(request)
	oauth = OAuthAPI()
	return JsonResponse(oauth.retrieve_token_from_jwt(jwt))
