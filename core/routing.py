from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from typing import Sequence, Dict, Union, Tuple
from core.helpers import pluralize, get_model_name
from django.urls import path
from django.db import models

ModelViewSetType = Union[ModelViewSet, ReadOnlyModelViewSet]

VIEWSET_METHODS = {
	'list': {
		'get': 'list',
		'post': 'create',
	},
	'detail': {
		'get': 'retrieve',
		'put': 'update',
		'patch': 'partial_update',
		'delete': 'destroy',
	},
}

CONVERTERS_MAP = {
	models.UUIDField: 'uuid',
	models.SlugField: 'slug',
	models.CharField: 'str',
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
		if isinstance(step, type) and issubclass(step, (ModelViewSet, ReadOnlyModelViewSet)):
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

def filter_viewset_methods(route_type: str, viewset: ModelViewSetType) -> Dict[str, str]:
	"""Helper to filter viewset methods for viewset.as_view usage"""
	return {
		method: action
		for method, action in VIEWSET_METHODS[route_type].items()
		if hasattr(viewset, action)
	}

def gen_url_set(viewsets: Union[ModelViewSetType, Sequence[ModelViewSetType]],
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
		'route': url.rsplit('/', 1)[0],  # Remove last model_pk
		'name': f"{name}-list",
		'view': viewset.as_view(filter_viewset_methods('list', viewset)),
		**path_options.get('list', path_options),
	}
	detail_params = {
		'route': url,
		'name': f"{name}-detail",
		'view': viewset.as_view(filter_viewset_methods('detail', viewset)),
		**path_options.get('detail', path_options),
	}

	return [ path(**route_params) for route_params in (list_params, detail_params) ]
