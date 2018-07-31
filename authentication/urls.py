from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import url, include

from woolly_api.settings import VIEWSET
from .views import UserViewSet, UserRelationshipView, UserTypeViewSet, AuthView, JWTView


# Configure Viewsets
user_list = UserViewSet.as_view(VIEWSET['list'])
user_detail = UserViewSet.as_view(VIEWSET['detail'])
user_type_list = UserTypeViewSet.as_view(VIEWSET['list'])
user_type_detail = UserTypeViewSet.as_view(VIEWSET['detail'])



# API endpoints
urlpatterns = {

	# ============================================
	# 	Authentification des utilisateurs
	# ============================================

	# Get login URL to log through Portail des Assos
	url(r'^auth/login$', AuthView.login, name = 'auth.login'),
	# Log user in  and get JWT
	url(r'^auth/callback$', AuthView.login_callback, name = 'auth.callback'),
	# Get User information
	url(r'^auth/me$', AuthView.me, name = 'auth.me'),
	# Revoke session, JWT and redirect to Portal's logout
	url(r'^auth/logout$', csrf_exempt(AuthView.logout), name = 'auth.logout'),
	
	# Get the JWT after login
	url(r'^auth/jwt$', JWTView.get_jwt, name = 'auth.jwt'),
	# Refresh JWT : TODO
	url(r'^auth/refresh$', JWTView.refresh_jwt, name = 'auth.refresh'),
	# Validate JWT : TODO
	url(r'^auth/validate$', JWTView.validate_jwt, name = 'auth.validate'),


	# Basic login/logout for Browsable API
	url(r'^auth/basic/', include('rest_framework.urls', namespace = 'rest_framework') ),



	# ============================================
	# 	Utilisateurs
	# ============================================

	# Users
	url(r'^users$',
		user_list, name = "user-list"),
	url(r'^users/(?P<pk>[0-9]+)$',
		user_detail, name = 'user-detail'),
	url(r'^users/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = UserRelationshipView.as_view(), name = 'user-relationships'
	),

	# UsersTypes
	url(r'^usertypes$',
		user_type_list, name = "usertype-list"),
	url(r'^usertypes/(?P<pk>[0-9]+)$',
		user_type_detail, name = 'usertype-detail'),
	url(r'^users/(?P<user_pk>[0-9]+)/usertypes$',
		user_type_list, name = 'usertype-list'),
	url(r'^users/(?P<user_pk>[0-9]+)/usertypes/(?P<pk>[0-9]+)$',
		user_type_detail, name = 'usertype-detail'),

}


urlpatterns = format_suffix_patterns(urlpatterns)
