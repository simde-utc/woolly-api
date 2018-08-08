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



def gen_base_url_set(resource_name, viewset, relationship_viewset = None):
	"""
	@brief      Helper to generate JSON API friendly url pattern set
	
	@param      resource_name         The string representing the resource in the url
	@param      viewset               The resource ModelViewSet
	@param      relationship_viewset  The resource RelationshipView
	
	@return     A list of url pattern
	"""

	list = {
		'regex': r'^' + resource_name + '$',
		'view': viewset.as_view(VIEWSET['list']),
		'name': resource_name + '-list',
	}

	# Simpler to use [^/.]+
	# detail_pk_regex = '[0-9a-f-]+' if pk_is_uuid else '[0-9]+'
	detail = {
		'regex': r'^' + resource_name + r'/(?P<pk>[^/.]+)$',
		'view': viewset.as_view(VIEWSET['detail']),
		'name': resource_name + '-detail',
	}
	set = [list, detail]

	if relationship_viewset is not None:
		relationships = {
			'regex': detail['regex'][:-1] + r'/relationships/(?P<related_field>[^/.]+)$',
			'view': relationship_viewset.as_view(),
			'name': resource_name + '-relationships',
		}
		set.append(relationships)
		print(detail)
		print(relationships)

	return [ url(**route) for route in set ]
