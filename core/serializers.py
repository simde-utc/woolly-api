from rest_framework.relations import ManyRelatedField
from rest_framework import serializers
from django.utils.module_loading import import_string
from collections import OrderedDict
from .helpers import filter_dict_keys

FIELD_KWARGS = serializers.LIST_SERIALIZER_KWARGS


class ModelSerializer(serializers.ModelSerializer):
	"""
	Supercharged Model Serializer
	- Can include nested sub-models serialized via context.include_map
		{
			'sub1': {},
			'sub2': {
				'a': {},
				'b': {},
			},
		}

	TODO:
		- Hide data on demand
		- Show only fields data
	"""
	included_serializers = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Import included serializers if need to include
		if 'include_map' in self._context:
			self.included_serializers = {
				key: import_string(ser) if type(ser) is str else ser
				for key, ser in self.included_serializers.items()
			}

	def get_fields(self):
		"""
		Override of rest_framework.serializers.ModelSerializer.get_fields
		Change normal related field for included ones if specified in include map
		Returns a dictionary of {field_name: field_instance}.	
		"""
		fields = super().get_fields()
		include_map = self._context.get('include_map')
		if not include_map:
			return fields

		# Update all included fields with included serializers
		for key, sub_map in include_map.items():
			if key not in fields:
				raise KeyError(f"Key '{key}' is not a declared field of {type(self).__name__}")

			included_serializer = self.included_serializers.get(key)
			if not included_serializer:
				raise KeyError(f"Key '{key}' is not attached in {type(self).__name__}.included_serializers")

			# Create and attach new serializer with right kwargs
			field_kwargs = filter_dict_keys(fields[key]._kwargs, FIELD_KWARGS)
			field_kwargs['many'] = isinstance(fields[key], ManyRelatedField)
			if 'context' not in field_kwargs:
				field_kwargs['context'] = {}
			field_kwargs['context']['include_map'] = sub_map

			# Update field with included serializer
			fields[key] = included_serializer(**field_kwargs)

		# Return updated fields
		return fields


class APIModelSerializer(ModelSerializer):
	"""
	ModelSerializer that can display additional data from APIModels
	"""
	id = serializers.UUIDField(format='hex_verbose', read_only=True)

	def to_representation(self, instance) -> dict:
		data = super().to_representation(instance)
		fetched_data = getattr(instance, 'fetched_data', None)
		if fetched_data:
			return OrderedDict({ **data, **fetched_data })
		return data
