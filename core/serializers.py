from typing import List
from collections import OrderedDict

from django.utils.module_loading import import_string
from rest_framework.exceptions import PermissionDenied
from rest_framework.relations import ManyRelatedField
from rest_framework import serializers

from .exceptions import InvalidRequest
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

    def get_field_names(self, declared_fields, info) -> List[str]:
        """
        Override of ModelSerializer.get_field_names
        Return only the required fields
        """
        all_fields = set(self.get_default_field_names(declared_fields, info))
        base_fields = getattr(self.Meta, 'fields')
        if not base_fields:
            raise Exception("Must specify Meta.fields")

        if base_fields == serializers.ALL_FIELDS:
            field_names = set(self.get_default_field_names(declared_fields, info))
        else:
            field_names = set(base_fields)

        # Add required fields
        additional_fields = self._context.get('with', [])
        include_tree = self._context.get('include_tree')
        if include_tree:
            additional_fields.extend(include_tree.keys())

        # Check requested fields are valid
        for field in additional_fields:
            if field not in all_fields:
                msg = f"Field '{field}' is not a valid field of {type(self).__name__}"
                raise InvalidRequest(msg, code="invalid_with_field")

            field_names.add(field)

        return list(field_names)

    def check_manager_rights_on_fields(self, fields: OrderedDict) -> None:
        """
        Check that fields comply with manager permissions
        """
        is_manager = getattr(self.context["request"], "is_manager", None)
        manager_fields = getattr(self.Meta, "manager_fields", set())

        for key in fields:
            if key in manager_fields and not is_manager:
                raise PermissionDenied(f"Cannot use '{key}' field")

    def get_fields(self) -> OrderedDict:
        """
        Override of rest_framework.serializers.ModelSerializer.get_fields
        Change normal related field for included ones if specified in include tree
        Returns a dictionary of {field_name: field_instance}.
        """
        fields = super().get_fields()
        include_tree = self._context.get('include_tree')
        if not include_tree:
            self.check_manager_rights_on_fields(fields)
            return fields

        # Update all included fields with included serializers
        for key, sub_tree in include_tree.items():
            if key not in fields:
                msg = f"Key '{key}' is not a declared field of {type(self).__name__}"
                raise InvalidRequest(msg, code="invalid_field")

            if key not in self.included_serializers:
                msg = f"Field '{key}' is not attached in {type(self).__name__}.included_serializers"
                raise InvalidRequest(msg, code="no_include_serializer")

            # Create and attach new serializer with right kwargs
            field_kwargs = filter_dict_keys(fields[key]._kwargs, FIELD_KWARGS)
            field_kwargs.setdefault('context', {})
            field_kwargs['context']['include_tree'] = sub_tree
            field_kwargs['many'] = isinstance(fields[key], ManyRelatedField)

            # Update field with included serializer
            fields[key] = self.included_serializers[key](**field_kwargs)

        # Return updated fields
        self.check_manager_rights_on_fields(fields)
        return fields


class APIModelSerializer(ModelSerializer):
    """
    ModelSerializer that can display additional data from APIModels
    """
    id = serializers.UUIDField(format='hex_verbose', read_only=True)

    def to_representation(self, instance) -> OrderedDict:
        data = super().to_representation(instance)
        fetched_data = getattr(instance, 'fetched_data', None)
        if fetched_data:
            return OrderedDict({ **data, **fetched_data })
        return data
