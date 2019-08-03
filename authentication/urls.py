from rest_framework.urlpatterns import format_suffix_patterns
from django.views.decorators.csrf import csrf_exempt
from django.urls import re_path, path, include

from core.helpers import gen_url_set, merge_sets
from .views import *


# JSON API Resource routes
urlpatterns = merge_sets(
	gen_url_set('users', UserViewSet),
	gen_url_set('usertypes', UserTypeViewSet),
	gen_url_set(['users', 'usertypes'], UserTypeViewSet),
)

# Addtionnal API endpoints for Authentication
urlpatterns += [
	re_path(r'auth/login/?',      AuthView.login,                 name='login'),
	re_path(r'auth/callback/?',   AuthView.login_callback,        name='login_callback'),
	path('auth/me',               AuthView.me,                    name='me'),
	path('auth/logout',           csrf_exempt(AuthView.logout),   name='logout'),

	# Only to get Login and Logout buttons in the BrowsableAPI, not actually working
  path('auth/', 				        include('rest_framework.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
