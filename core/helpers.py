from django.http import JsonResponse
from rest_framework import status
from django.urls import re_path, path # TODO
from django.db import models

from rest_framework.viewsets import ModelViewSet
from typing import Sequence, Dict, Union, Tuple

NestedPath = Union[str, Sequence[str]]


def filter_dict_keys(obj: dict, whitelist: Sequence):
	return { k: v for k, v in obj.items() if k in whitelist }


def errorResponse(message, errors=tuple(), httpStatus=status.HTTP_400_BAD_REQUEST):
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


# --------------------------------------------------------------------------
# 		Naming
# --------------------------------------------------------------------------

def pluralize(name: str) -> str:
	return name + 's'

def get_model_name(instance) -> str:
	return (instance if isinstance(instance, type) else type(instance)).__name__.lower()


# --------------------------------------------------------------------------
# 		Routing
# --------------------------------------------------------------------------

VIEWSET_METHODS = {
	'list': {
		'get': 'list',
		'post': 'create'
	},
	'detail': {
		'get': 'retrieve',
		'put': 'update',
		'patch': 'partial_update',
		'delete': 'destroy'
	}
}

CONVERTERS_MAP = {
	models.UUIDField: 'uuid',
	models.SlugField: 'slug',
}

def merge_sets(*sets):
	return [ route for set in sets for route in set ]

def _get_names_and_model(step) -> str:
	"""
	Helper to get singular and plural names with model if possible
	"""
	singular = model = None
	if type(step) is str:
		singular = step
	else:
		if isinstance(step, type) and issubclass(step, ModelViewSet):
			model = step.queryset.model
		else:
			model = step
		singular = get_model_name(model)

	return singular, pluralize(singular), model

def build_nested_url(path: NestedPath, converters: Dict[str, str]={}) -> Tuple[str, str]:
	"""
	Build a nested url of the following shape:
	[step_plural/<(uuid,int,...):step_singular/<():pk>]resource_plural
	"""
	if type(path) is str:
		path = [path]

	last_i = len(path) - 1
	url, name = [], []
	for i, step in enumerate(path):
		singular, plural, model = _get_names_and_model(step)

		# Get the right converter
		if model:
			converter = CONVERTERS_MAP.get(type(model._meta.pk))
		converter = converters.get(singular, converter or 'int')

		# Build the step
		var = f"{converter}:" + (f"{singular}_pk" if i != last_i else 'pk')
		url.append(f"{plural}/<{var}>")
		name.append(plural)

	return '/'.join(url), '-'.join(name)


def gen_url_set_2(viewsets: Sequence[ModelViewSet], **kwargs):
	"""
	Generate a set of URLs with the right paths and names
	from the list of nested viewsets
	"""

	# Build base url route & name
	url, name = build_nested_url(viewsets, kwargs.get('converters', {}))

	# Build url patterns
	viewset = viewsets[-1]
	path_options = kwargs.get('path_options', {})
	list = {
		'route': url.rsplit('/', 1)[0], 	# Remove last model_pk 
		'name': f"{name}-list",
		'view': viewset.as_view(VIEWSET_METHODS['list']),
		**path_options.get('list', path_options),
	}
	detail = {
		'route': url,
		'name': f"{name}-detail",
		'view': viewset.as_view(VIEWSET_METHODS['detail']),
		**path_options.get('detail', path_options),
	}

	return [ re_path(**route_params) for route_params in (list, detail) ]


def gen_url_set(path, viewset):
	"""
	@brief      Helper to easily generate the right url pattern set
	
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
		'view': viewset.as_view(VIEWSET_METHODS['list']),
		'name': base_name + '-list',
	}

	# Simpler to use [^/.]+
	# detail_pk_regex = '[0-9a-f-]+' if pk_is_uuid else '[0-9]+'
	detail = {
		'route': base_url + r'/(?P<pk>[^/.]+)$',
		'view': viewset.as_view(VIEWSET_METHODS['detail']),
		'name': base_name + '-detail',
	}

	return [ re_path(**route) for route in (list, detail) ]
