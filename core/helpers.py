from typing import Sequence, Iterable, Callable
from django.utils import timezone

CURRENT_TZ = timezone.get_current_timezone()

# --------------------------------------------------------------------------
# 		Data Structures
# --------------------------------------------------------------------------

def filter_dict_keys(obj: dict, whitelist: Sequence) -> dict:
	"""
	Filter dictionnary keys from a whitelist
	
	Args:
		obj: the dictionnary to filter
		whitelist: the whitelist of keys to keep

	Returns:
		dict: the filtered dictionnary
	"""
	return { k: v for k, v in obj.items() if k in whitelist }

def iterable_to_map(iterable: Iterable, get_key: Callable=None, prop: str=None, attr: str=None) -> dict:
	"""
	Change an iterable into a dictionnary by selecting a key from each item
	
	Args:
		iterable (Iterable): the iterable to transform
		get_key: a function that takes an item and return its key
		prop (str): the property to get the key from with item[prop]
		attr (str): the attribute to get the key from with getattr(item, attr)
	
	Raises:
		ValueError: if prop, attr or get_key are all None

	Returns:
		dict: the mapped iterable
	"""
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

# --------------------------------------------------------------------------
# 		Models
# --------------------------------------------------------------------------

def get_field_default_value(default: str, order: 'Order'):
	"""
	Get the default value of a field
	"""
	return {
		'owner.first_name': order.owner.first_name,
		'owner.last_name': order.owner.last_name,
	}.get(default, default)

def adaptable_editability_fields(obj=None, edition_readonly: Sequence=[], always_readonly: Sequence=[]) -> tuple:
	"""
	Helper to allow non editable fields to be set on creation
	"""
	return tuple(always_readonly if obj is None else edition_readonly)

# --------------------------------------------------------------------------
# 		Naming
# --------------------------------------------------------------------------

def pluralize(name: str) -> str:
	"""
	Simple and quite stupid helper to pluralize a name
	"""
	return name + 's'

def get_model_name(inst) -> str:
	"""
	Get the lowered model name from an instance
	"""
	return (inst if isinstance(inst, type) else type(inst)).__name__.lower()
