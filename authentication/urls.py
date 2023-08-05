from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt
from django.urls import re_path, include

from core.helpers import gen_url_set, merge_sets
from .views import *


# JSON API Resource routes
urlpatterns = merge_sets(
	gen_url_set('users', UserViewSet, UserRelationshipView),
	gen_url_set('usertypes', UserTypeViewSet, UserTypeRelationshipView),
	gen_url_set(['users', 'usertypes'], UserTypeViewSet),
)

# Addtionnal API endpoints for Authentication
urlpatterns += [

	# Get login URL to log through Portail des Assos
	re_path(r'^auth/login$', AuthView.login, name = 'auth.login'),
	# Log user in  and get JWT
	re_path(r'^auth/callback$', AuthView.login_callback, name = 'auth.callback'),
	# Get User information
	re_path(r'^auth/me$', AuthView.me, name = 'auth.me'),
	# Revoke session, JWT and redirect to Portal's logout
	re_path(r'^auth/logout$', csrf_exempt(AuthView.logout), name = 'auth.logout'),
	
	# Get the JWT after login
	re_path(r'^auth/jwt$', JWTView.get_jwt, name = 'auth.jwt'),
	# Refresh JWT : TODO
	re_path(r'^auth/refresh$', JWTView.refresh_jwt, name = 'auth.refresh'),
	# Validate JWT : TODO
	re_path(r'^auth/validate$', JWTView.validate_jwt, name = 'auth.validate'),

	# Basic login/logout for Browsable API
	re_path(r'^auth/basic/', include('rest_framework.urls', namespace = 'rest_framework') ),

]


urlpatterns = format_suffix_patterns(urlpatterns)
