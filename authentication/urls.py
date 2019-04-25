from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import url, include

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
	url(r'^auth/login$', AuthView.login, name='auth.login'),
	# Log user in  and get JWT
	url(r'^auth/callback$', AuthView.login_callback, name='auth.callback'),
	# Get User information
	url(r'^auth/me$', AuthView.me, name='auth.me'),
	# Revoke session, JWT and redirect to Portal's logout
	url(r'^auth/logout$', csrf_exempt(AuthView.logout), name='auth.logout'),

	# Basic login/logout for Browsable API
	url(r'^auth/basic/', include('rest_framework.urls', namespace='rest_framework')),

]


urlpatterns = format_suffix_patterns(urlpatterns)
