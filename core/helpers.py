from django.http import JsonResponse
from rest_framework import status
from woolly_api.settings import VIEWSET
from django.conf.urls import url

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


def gen_url_set(path, viewset, relationship_viewset=None):
	"""
	@brief      Helper to generate JSON API friendly url pattern set
	
	@param      resource_name         The string representing the resource in the url
	@param      viewset               The resource ModelViewSet
	@param      relationship_viewset  The resource RelationshipView
	
	@return     A list of url pattern
	"""

	# TODO if for nested vs relationship_viewset

	# ===== Build base url
	base_url = r'^'
	base_name = ''
	for step in path[:-1]:
		# Pluralize the resource name for the url
		plural = step + 's' if type(step) is str else step[1]

		# Build base url regex
		base_url += plural + r'/(?P<' + step + r'_pk>[0-9]+)/'

		# Build base route name
		base_name += plural + '-'

	resource_name = path[-1]
	plural = resource_name + 's' if type(resource_name) is str else resource_name[1]
	base_url += plural
	base_name += plural

	# ===== Build url patterns
	list = {
		'regex': base_url + '$',
		'view': viewset.as_view(VIEWSET['list']),
		'name': base_name + '-list',
	}

	# Simpler to use [^/.]+
	# detail_pk_regex = '[0-9a-f-]+' if pk_is_uuid else '[0-9]+'
	detail = {
		'regex': base_url + r'/(?P<pk>[^/.]+)$',
		'view': viewset.as_view(VIEWSET['detail']),
		'name': base_name + '-detail',
	}
	set = [list, detail]

	if relationship_viewset is not None:
		relationships = {
			'regex': base_url + r'/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
			'view': relationship_viewset.as_view(),
			'name': base_name + '-relationships',
		}
		set.append(relationships)

	return [ url(**route) for route in set ]


