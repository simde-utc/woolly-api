from django.http import JsonResponse
from rest_framework import status

from woolly_api.settings import VIEWSET
from django.conf.urls import re_path

def filter_dict_keys(obj: dict, whitelist):
	return { k: v for k, v in obj.items() if k in whitelist }


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

def get_resource_name(instance):
	return (instance if isinstance(instance, type) else type(instance)).__name__.lower() + 's'

def gen_url_set(path, viewset):
	"""
	@brief      Helper to generate JSON API friendly url pattern set
	
	@param      path                 The string representing the resource in the url (plural)
	@param      viewset               The resource ModelViewSet
	
	@return     A list of url pattern
	"""

	# ===== Build base url
	if type(path) is str:       # Simple version
		base_url = r'^' + path
		base_name = path
	else:                       # Nested version
		base_url = r'^'
		base_name = ''

		for step in path[:-1]:
			# Build base url route & name
			base_url += step + r'/(?P<' + step + r'_pk>[^/.]+)/'
			base_name += step + '-'

		resource_name = path[-1]
		base_url += resource_name
		base_name += resource_name
	# TODO Assert last step is resource_name
	# TODO gen_url_set(*viewsets)

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

	return [ re_path(**route) for route in (list, detail) ]
