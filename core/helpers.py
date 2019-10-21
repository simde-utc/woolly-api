from typing import Sequence, Iterable, Callable
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

CURRENT_TZ = timezone.get_current_timezone()

# --------------------------------------------------------------------------
# 		Data Structures
# --------------------------------------------------------------------------

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

def format_date(date) -> 'datetime':
	"""
	Format a date with the proper timezone
	"""
	if timezone.is_aware(date):
		return date
	else:
		return timezone.make_aware(date, CURRENT_TZ, is_dst=False)

def custom_editable_fields(request, obj=None, edition_readonly_fields=tuple(), always_readonly_fields=tuple()):
	"""
	Helper to allow non editable fields to be set on creation
	"""
	return edition_readonly_fields if obj else always_readonly_fields

# --------------------------------------------------------------------------
# 		HTTP & REST
# --------------------------------------------------------------------------

def ErrorResponse(error: str, detail: Sequence[str]=[], status=status.HTTP_400_BAD_REQUEST) -> Response:
	data = {
		'error': str(error),
		'detail': detail,
	}
	return Response(data, status=status)

# --------------------------------------------------------------------------
# 		Naming
# --------------------------------------------------------------------------

def pluralize(name: str) -> str:
	return name + 's'

def get_model_name(instance) -> str:
	return (instance if isinstance(instance, type) else type(instance)).__name__.lower()

