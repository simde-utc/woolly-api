from rest_framework.relations import ManyRelatedField
from rest_framework import serializers
from .helpers import import_class

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
	"""
	included_serializer = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._declared_fields = self.update_included(self._declared_fields)
		import pdb; pdb.set_trace()
		# print("-- ModelSerializer.__init__ -- ", self.__class__.__name__)

	def update_included(self, fields):
		"""
		Change normal related field for included ones if specified in query params
		"""
		# Check if include is in request and not empty
		if 'request' not in self.context:
			return fields

		include_map = self.context.get('include_map')
		if not include_map:
			return fields

		print("Included map")
		from pprint import pprint as pp
		import pdb; pdb.set_trace()
		pp(fields)

		fields = fields.copy()
		# Update all included fields
		for key, sub_map in include_map.items():
			included_serializer = self.included_serializers.get(key)

			# Import and override the serializer if there
			if included_serializer:
				# Import included serializer if needed
				if type(included_serializer) is str:
					included_serializer = import_class(included_serializer)

				# Create and attach new serializer with right kwargs
				field_kwargs = { kw: value
											 for kw, value in fields[key]._kwargs.items()
											 if kw in FIELD_KWARGS }
				field_kwargs['many'] = isinstance(fields[key], ManyRelatedField)

				# Add sub_map if needed
				if sub_map:
					if 'context' not in field_kwargs:
						field_kwargs['context'] = {}
					field_kwargs['context']['include_map'] = sub_map
					
				import pdb; pdb.set_trace()

				if self.instance is not None:
					# field_kwargs['instance'] = 
					pass



				fields[key] = included_serializer(**field_kwargs)


				fields[key] = serializer

		# Return updated fields
		import pdb; pdb.set_trace()
		pp(fields)
		return fields
