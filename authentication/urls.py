from django.urls import re_path, path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.urlpatterns import format_suffix_patterns

from core.routing import gen_url_set, merge_sets
from authentication.views import AuthView, UserViewSet, UserTypeViewSet
from sales.views import AssociationViewSet, OrderViewSet


urlpatterns = merge_sets(
    # User
    gen_url_set(UserViewSet),
    gen_url_set([UserViewSet, AssociationViewSet]),
    gen_url_set([UserViewSet, OrderViewSet]),

    # Usertype
    gen_url_set(UserTypeViewSet),
)

# Addtionnal API endpoints for Authentication
urlpatterns += [
    re_path(r'auth/login/?',      AuthView.login,                 name='login'),
    re_path(r'auth/callback/?',   AuthView.login_callback,        name='login_callback'),
    path('auth/me',               AuthView.me,                    name='me'),
    path('auth/logout',           csrf_exempt(AuthView.logout),   name='logout'),

    # Only to get Login and Logout buttons in the BrowsableAPI, not actually working
    path('auth/',                 include('rest_framework.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
