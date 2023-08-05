from django.http import JsonResponse
from rest_framework import status

from rest_framework_json_api.relations import ResourceRelatedField
from woolly_api.settings import VIEWSET
from django.urls import re_path

def errorResponse(message, errors = tuple(), httpStatus = status.HTTP_400_BAD_REQUEST):
	resp = {
		'message': message,
		'errors': [ {'detail': e} for e in errors ]
	}
	return JsonResponse(resp, status=httpStatus)


def custom_editable_fields(request, obj=None, edition_readonly_fields=tuple(), always_readonly_fields=tuple()):
	"""
	Helper to allow non editable fields to be set on creation
	"""
	return edition_readonly_fields if obj else always_readonly_fields


def merge_sets(*sets):
	return [ route for set in sets for route in set ]

def gen_url_set(path, viewset, relationship_viewset=None):
	"""
	@brief      Helper to generate JSON API friendly url pattern set
	
	@param      resource_name         The string representing the resource in the url (plural)
	@param      viewset               The resource ModelViewSet
	@param      relationship_viewset  The resource RelationshipView
	
	@return     A list of url pattern
	"""

	# ===== Build base url
	if type(path) is str:				# Simple version
		base_url = r'^' + path
		base_name = path
	else:								# Nested version
		base_url = r'^'
		base_name = ''

		for step in path[:-1]:
			# Build base url route & name
			base_url += step + r'/(?P<' + step + r'_pk>[^/.]+)/'
			base_name += step + '-'

		resource_name = path[-1]
		base_url += resource_name
		base_name += resource_name

	# ===== Build url patterns
	list = {
		'route': base_url + '$',
		'view': viewset.as_view(VIEWSET['list']),
		'name': base_name + '-list',
	}

	# Simpler to use [^/.]+
	# detail_pk_regex = '[0-9a-f-]+' if pk_is_uuid else '[0-9]+'
	detail = {
		'route': base_url + r'/(?P<pk>[^/.]+)$',
		'view': viewset.as_view(VIEWSET['detail']),
		'name': base_name + '-detail',
	}
	set = [list, detail]

	if relationship_viewset is not None:
		relationships = {
			'route': base_url + r'/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
			'view': relationship_viewset.as_view(),
			'name': base_name + '-relationships',
		}
		set.append(relationships)

	return [ re_path(**route) for route in set ]


def get_ResourceRelatedField(parent, child, queryset = None, read_only = False, many = False, **kwargs):
	route_type = 'list' # if many else 'detail'
	params = {
		'many': many,
		'related_link_view_name': "%s-%s-%s" % (parent, child, route_type),
		'related_link_url_kwarg': parent + "_pk",
		'self_link_view_name': parent + '-relationships',
		**kwargs
	}
	if queryset is None or read_only is True:
		params['read_only'] = True
	else:
		params['queryset'] = queryset

	return ResourceRelatedField(**params)
