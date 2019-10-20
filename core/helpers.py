from django.http import JsonResponse
from rest_framework import status
from typing import Sequence, Iterable, Callable


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

