from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from authentication.views import WoollyUserViewSet, WoollyUserRelationshipView, WoollyUserTypeViewSet
import cas.views
from . import views


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
	# CAS login/logout
	url(r'^cas/login$', cas.views.login, name='cas.login'),
	url(r'^cas/logout$', cas.views.logout, name='cas.logout'),

	# Basic login/logout
	url(r'^auth/', include('rest_framework.urls', namespace='rest_framework') ),

	# WoollyUsers
	url(r'^users',
		woollyuser_list,
		name="user-list"),
	url(r'^users/(?P<pk>[0-9]+)$',
		woollyuser_detail,
		name='user-detail'),
	url(r'^users/me', views.userInfos), # "/store" will call the method "index" in "views.py"

	# WoollyUsersTypes
	url(r'^users/(?P<user_pk>[0-9]+)/woollyusertypes$',
		user_type_list,
		name='user-type-list'),
	url(r'^users/(?P<user_pk>[0-9]+)/woollyusertypes/(?P<pk>[0-9]+)$',
		user_type_detail,
		name='user-type-detail'),
	# OR ????
	# WoollyUsersTypes
	url(r'^woollyusertypes',
		user_type_list,
		name="user-type-list"),
	url(r'^woollyusertypes/(?P<pk>[0-9]+)$',
		user_type_detail,
		name='user-type-detail'),

	url(
		regex=r'^users/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view=WoollyUserRelationshipView.as_view(),
		name='user-relationships'
	),

}


urlpatterns = format_suffix_patterns(urlpatterns)
