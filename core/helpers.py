from django.http import JsonResponse
from rest_framework import status
from django.urls import path
from django.db import models

from rest_framework.viewsets import ModelViewSet
from typing import Sequence, Dict, Union, Tuple, Iterable, Callable


def filter_dict_keys(obj: dict, whitelist: Sequence):
	return { k: v for k, v in obj.items() if k in whitelist }

def iterable_to_map(iterable: Iterable, prop: str=None, attr: str=None, get_key: Callable=None) -> dict:
	if not get_key:
		if prop:
			get_key = lambda obj: obj[prop]
		elif attr:
			get_key = lambda obj: getattr(obj, attr)
		else:
			raise ValueError("At least one of 'prop', 'attr' or 'get_key' must be provided")
	return { get_key(obj): obj for obj in iterable }

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

def build_nested_url(path, converters: Dict[str, str]={}) -> Tuple[str, str]:
	"""
	Build a nested url of the following shape:
	[step_plural/<(uuid,int,...):step_singular>]/resource_plural/<(...):pk>
	"""
	if not isinstance(path, (list, tuple)):
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

def gen_url_set(viewsets: Union[ModelViewSet, Sequence[ModelViewSet]],
								converters: Dict[str, str]={}, path_options: dict={}):
	"""
	Generate a set of URLs with the right paths and names
	from the list of nested viewsets
	"""
	# Build base url route & name
	url, name = build_nested_url(viewsets, converters)

	# Build url patterns
	viewset = viewsets[-1] if isinstance(viewsets, (list, tuple)) else viewsets
	list_params = {
		'route': url.rsplit('/', 1)[0], 	# Remove last model_pk 
		'name': f"{name}-list",
		'view': viewset.as_view(VIEWSET_METHODS['list']),
		**path_options.get('list', path_options),
	}
	detail_params = {
		'route': url,
		'name': f"{name}-detail",
		'view': viewset.as_view(VIEWSET_METHODS['detail']),
		**path_options.get('detail', path_options),
	}

	return [ path(**route_params) for route_params in (list_params, detail_params) ]
