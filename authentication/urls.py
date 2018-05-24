from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns
from .views import WoollyUserViewSet, WoollyUserRelationshipView, WoollyUserTypeViewSet, AuthView, JWTView
import cas.views


woollyuser_list = WoollyUserViewSet.as_view({
	'get': 'list',
	'post': 'create'
})
woollyuser_detail = WoollyUserViewSet.as_view({
	'get': 'retrieve',
	'put': 'update',
	'patch': 'partial_update',
	'delete': 'destroy'
})
user_type_list = WoollyUserTypeViewSet.as_view({
	'get': 'list',
	'post': 'create'
})
user_type_detail = WoollyUserTypeViewSet.as_view({
	'get': 'retrieve',
	'put': 'update',
	'patch': 'partial_update',
	'delete': 'destroy'
})



# API endpoints
urlpatterns = {

	# ============================================
	# 	Authentification des utilisateurs
	# ============================================

	# Get login URL to log through Portail des Assos
	url(r'^auth/login', AuthView.login, name = 'auth.login'),
	# Log user in Woolly and get JWT
	url(r'^auth/callback', AuthView.login_callback, name = 'auth.callback'),
	# Get User information
	url(r'^auth/me', AuthView.me, name = 'auth.me'),
	# Revoke session, JWT and redirect to Portal's logout
	url(r'^auth/logout', csrf_exempt(AuthView.logout), name = 'auth.logout'),
	
	# Get the JWT after login
	url(r'^auth/jwt$', JWTView.get_jwt, name = 'auth.jwt'),
	# Refresh JWT : TODO
	url(r'^auth/refresh', JWTView.refresh_jwt, name = 'auth.refresh'),
	# Validate JWT : TODO
	url(r'^auth/validate', JWTView.validate_jwt, name = 'auth.validate'),





	# ==== TODO A virer...
	# CAS login/logout
	url(r'^auth/cas/login$', cas.views.login, name = 'cas.login'),
	url(r'^auth/cas/logout$', cas.views.logout, name = 'cas.logout'),

	# Basic login/logout
	url(r'^auth/basic/', include('rest_framework.urls', namespace = 'rest_framework') ),



	# ============================================
	# 	Utilisateurs
	# ============================================

	# WoollyUsers
	url(r'^users',
		woollyuser_list,
		name = "user-list"),
	url(r'^users/(?P<pk>[0-9]+)$',
		woollyuser_detail,
		name = 'user-detail'),

	# WoollyUsersTypes
	url(r'^users/(?P<user_pk>[0-9]+)/woollyusertypes$',
		user_type_list,
		name = 'user-type-list'),
	url(r'^users/(?P<user_pk>[0-9]+)/woollyusertypes/(?P<pk>[0-9]+)$',
		user_type_detail,
		name = 'user-type-detail'),
	# OR ????
	# WoollyUsersTypes
	url(r'^woollyusertypes',
		user_type_list,
		name = "user-type-list"),
	url(r'^woollyusertypes/(?P<pk>[0-9]+)$',
		user_type_detail,
		name = 'user-type-detail'),

	url(
		regex = r'^users/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = WoollyUserRelationshipView.as_view(),
		name = 'user-relationships'
	),

}


urlpatterns = format_suffix_patterns(urlpatterns)
