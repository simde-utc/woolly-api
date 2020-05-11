from rest_framework.relations import ManyRelatedField
from rest_framework import serializers
from django.utils.module_loading import import_string
from collections import OrderedDict
from .helpers import filter_dict_keys

FIELD_KWARGS = serializers.LIST_SERIALIZER_KWARGS


class ModelSerializer(serializers.ModelSerializer):
    """
    Supercharged Model Serializer
    - Can include nested sub-models serialized via context.include_tree
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
        if 'include_tree' in self._context:
            self.included_serializers = {
                key: import_string(ser) if type(ser) is str else ser
                for key, ser in self.included_serializers.items()
            }

    def get_fields(self) -> dict:
        """
        Override of rest_framework.serializers.ModelSerializer.get_fields
        Change normal related field for included ones if specified in include tree
        Returns a dictionary of {field_name: field_instance}.
        """
        fields = super().get_fields()
        include_tree = self._context.get('include_tree')
        if not include_tree:
            return fields

        # Update all included fields with included serializers
        for key, sub_tree in include_tree.items():
            if key not in fields:
                raise KeyError(f"Key '{key}' is not a declared field of {type(self).__name__}")

            included_serializer = self.included_serializers.get(key)
            if not included_serializer:
                raise KeyError(f"Key '{key}' is not attached in {type(self).__name__}.included_serializers")

            # Create and attach new serializer with right kwargs
            field_kwargs = filter_dict_keys(fields[key]._kwargs, FIELD_KWARGS)
            field_kwargs.setdefault('context', {})
            field_kwargs['context']['include_tree'] = sub_tree
            field_kwargs['many'] = isinstance(fields[key], ManyRelatedField)

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
