from rest_framework.response import Response
from rest_framework import viewsets
from authentication.oauth import OAuthAPI


class ModelViewSetMixin(object):
	"""
	Supercharged DRF ModelViewSet
	- Automatic sub urls filterings (ex: assos/1/sales)
	- Automatic included sub resources prefetching (ex: sales?include=items,items__group)

	TODO:
	- Filter permissions per objet
	- Creation with nested urls
	- Security checks
	"""

	def query_params_is_true(self, key: str) -> bool:
		"""
		Whether the request as the specified params and it is not false
		"""
		value = self.request.GET.get(key)
		return value is None or value.lower() != 'false'

	def get_queryset(self):
		"""
		Override from GenericAPIView
		"""
		queryset = super().get_queryset()

		# Prefetch included sub models
		include_query = self.request.GET.get('include')
		if include_query:
			queryset = queryset.prefetch_related(*include_query.split(','))

		# Filter according to sub urls
		nested_url_filters = self.get_sub_urls_filters(queryset)
		if nested_url_filters:
			queryset = queryset.filter(**nested_url_filters)

		# TODO Filter permission ??

		return queryset

	def get_sub_urls_filters(self, queryset) -> dict:
		"""
		Return queryset filters for sub urls
		Can be easily overriden for special naming (ie. Order.owner = User)
		"""
		return {
			key.replace('_pk', '__pk'): value
			for key, value in self.kwargs.items()
		}

	# def get_object(self):
	# 	return super().get_object()

	def get_serializer_context(self) -> dict:
		"""
		Pass the include_map to the serializer
		"""
		include_query = self.request.GET.get('include')
		return {
			**super().get_serializer_context(),
			'include_map': self.get_include_map(include_query),
		}

	@staticmethod
	def get_include_map(include_query: str) -> dict:
		"""
		Create a include map for nested serializers from query
		query: include=sub1,sub2,sub2__a,sub2__b
		map: {
			'sub1': {},
			'sub2': {
				'a': {},
				'b': {},
			},
		}
		"""
		if not include_query:
			return None

		include_map = {}
		for path in include_query.split(','):
			current_map = include_map
			for step in path.split('__'):
				if step not in current_map:
					current_map[step] = {}
				current_map = current_map[step]

		return include_map

	# def handle_exception(self, exc):
	# 	"""Override from APIView"""
	# 	return super().handle_exception(exc)


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
