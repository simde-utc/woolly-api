from typing import Any, List

from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework import viewsets

from authentication.oauth import OAuthAPI
from .exceptions import InvalidRequest


class ModelViewSetMixin(object):
    """
    Supercharged DRF ModelViewSet
    - Filter nested-urls (ex: /associations/1/sales)
    - Include nested-resources prefetching (ex: /sales?include=items,items__group)
    - Filter on specified values (ex: /orders?filter=status__in=2,4&filter=id__gt=2)
    - Order as specified

    TODO:
    - Filter permissions per objet
    - Creation with nested urls
    - Security checks
    - Error checking from query
    - Parse query params to the right type
    """

    # Helpers

    def query_params_is_true(self, key: str) -> bool:
        """
        Whether the request as the specified params and it is not false
        """
        value = self.request.GET.get(key)
        return value is None or value.lower() != 'false'

    def get_kwarg(self, kwarg_key: str, data_key: str, default_value: Any=None) -> Any:
        return self.kwargs.get(kwarg_key, self.request.data.get(data_key, default_value))

    @staticmethod
    def get_include_tree(query: dict) -> dict:
        """
        Create a include map for nested serializers from comma-separated values in query
        query: { include: 'sub1,sub2,sub2__a,sub2__b', select: 'sub3' }
        map: {
            'sub1': {},
            'sub2': {
                'a': {},
                'b': {},
            },
            'sub3': {}
        }
        """
        include_list = []
        if query.get('include'):
            include_list.extend(query['include'].split(','))
        if query.get('select'):
            include_list.extend(query['select'].split(','))

        if not include_list:
            return None

        include_tree = {}
        for path in include_list:
            current_map = include_tree
            for step in path.split('__'):
                if step not in current_map:
                    current_map[step] = {}
                current_map = current_map[step]

        return include_tree

    @staticmethod
    def get_with_fields(query: dict) -> List[str]:
        with_fields = query.get('with')
        if with_fields:
            return with_fields.split(',')
        return []

    def get_sub_urls_filters(self, queryset: QuerySet) -> dict:
        """
        Return queryset filters for sub urls
        Can be easily overriden for special naming (ie. Order.owner = User)
        """
        return {
            key.replace('_pk', '__pk'): value
            for key, value in self.kwargs.items()
        }

    def get_serializer_context(self) -> dict:
        """
        Pass the include_tree to the serializer
        """
        return {
            **super().get_serializer_context(),
            'include_tree': self.get_include_tree(self.request.GET),
            'with': self.get_with_fields(self.request.GET),
        }

    def parse_query_param_value(self, key: str, value: str) -> Any:
        _type = str

        if key.endswith('__in'):
            value = list(map(_type, value.split(',')))

        return value

    # QuerySet filtering

    def include_sub_models(self, queryset: QuerySet) -> QuerySet:
        """
        Prefetch data required in the query for better performance
        """
        # Prefetch many data
        include_query = self.request.GET.get('include')
        if include_query:
            queryset = queryset.prefetch_related(*include_query.split(','))

        # Select one data
        select_query = self.request.GET.get('select')
        if select_query:
            queryset = queryset.select_related(*select_query.split(','))

        return queryset

    def filter_by_sub_urls(self, queryset: QuerySet) -> QuerySet:
        """
        Filter queryset base on url nesting
        For example: /users/1/associations
        """
        nested_url_filters = self.get_sub_urls_filters(queryset)
        if nested_url_filters:
            queryset = queryset.filter(**nested_url_filters)

        return queryset

    def filter_from_query_params(self, queryset: QuerySet) -> QuerySet:
        """
        Filter queryset based on field and values specified
        /orders?filter=status__in=2,4&filter=id__gt=2
        """
        filters_query = self.request.GET.getlist('filter')
        if filters_query:
            # Parse filters
            filter_params = {}
            for _filter in filters_query:
                key, value = _filter.split('=', 1)
                filter_params[key] = self.parse_query_param_value(key, value)

            queryset = queryset.filter(**filter_params)

        return queryset

    def order_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Order the data as specified by the query
        """
        order_query = self.request.GET.get('order_by')
        if order_query:
            queryset = queryset.order_by(*order_query.split(','))

        return queryset

    def get_queryset(self) -> QuerySet:
        """
        Override from GenericAPIView
        """
        queryset = super().get_queryset()

        # Prefetch included sub models
        queryset = self.include_sub_models(queryset)

        # Filter according to sub urls
        queryset = self.filter_by_sub_urls(queryset)

        # Filter according to query params
        queryset = self.filter_from_query_params(queryset)

        # TODO Filter sub permission ??

        # Order
        queryset = self.order_queryset(queryset)

        return queryset

    def paginate_queryset(self, *args, **kwargs):
        try:
            return super().paginate_queryset(*args, **kwargs)
        except AttributeError as error:
            key = str(error).split('\'', 2)[1]
            msg = f"Key '{key}' is not a valid field of {self.queryset.model.__name__}"
            raise InvalidRequest(msg, code="invalid_field")


class ModelViewSet(ModelViewSetMixin, viewsets.ModelViewSet):
    pass


class APIModelViewSet(ModelViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Supercharged ReadOnlyModelViewSet linked to an external OAuth API
    """

    @property
    def oauth_client(self) -> OAuthAPI:
        """
        Get OAuthClient from request's session
        """
        return OAuthAPI(session=self.request.session)

    def list(self, request, *args, **kwargs):
        """
        List and paginate APIModel with additional data
        """
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.get_with_api_data(self.oauth_client, single_result=False, **kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Try to retrieve APIModel from cache
        else fetch it with additional data
        """
        instance = self.queryset.model.get_from_cache(kwargs, single_result=True)

        if not getattr(instance, 'fetched_data', None):
            instance = self.get_object()
            instance.get_with_api_data(self.oauth_client)
        else:
            # Check permission manually if not going through get_object
            self.check_object_permissions(self.request, instance)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
