from rest_framework.relations import ManyRelatedField
from rest_framework import serializers
from .helpers import import_class

FIELD_KWARGS = serializers.LIST_SERIALIZER_KWARGS

class ModelSerializer(serializers.ModelSerializer):
	"""
	Todo:
		- Check permissions
		- Nested filtering
		- Include nested if possible
	"""
	included_serializer = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._declared_fields = self.update_included(self._declared_fields)

	def update_included(self, fields):
		"""
		Change normal related field for included ones if specified in query params
		"""
		# Check if include is in request and not empty
		if 'request' not in self.context:
			return fields
		include_list = self.context['request'].query_params.get('include', '').split(',')
		if not include_list:
			return fields

		fields = fields.copy()
		# Update all included fields
		for include_name in include_list:
			included_serializer = self.included_serializers.get(include_name)

			# Import and override the serializer if there
			if included_serializer:
				# Import included serializer if needed
				if type(included_serializer) is str:
					included_serializer = import_class(included_serializer)

				# Create and attach new serializer with right kwargs
				field_args = { key: value
											 for key, value in fields[include_name]._kwargs.items()
											 if key in FIELD_KWARGS }
				field_args['many'] = isinstance(fields[include_name], ManyRelatedField)
				fields[include_name] = included_serializer(**field_args)

		# Return updated fields
		return fields
