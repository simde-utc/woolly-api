from rest_framework.response import Response
from rest_framework import viewsets
from django.core.cache import cache
from core.models import gen_model_key

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

class ApiModelViewSet(ModelViewSetMixin, viewsets.ReadOnlyModelViewSet):
	"""
	Supercharged ReadOnlyModelViewSet linked to an external OAuth API
	"""
	_oauth_client = None

	@property
	def oauth_client(self):
		if self._oauth_client is None:
			from authentication.oauth import OAuthAPI
			self._oauth_client = OAuthAPI(session=self.request.session)
		return self._oauth_client

	def list(self, request, *args, **kwargs):
		"""
		List and paginate ApiModel with additional data
		"""
		queryset = self.filter_queryset(self.get_queryset())
		queryset = queryset.get_with_api_data(self.oauth_client, **kwargs)
		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)

	def retrieve(self, request, *args, **kwargs):
		"""
		Try to retrieve ApiModel from cache
		else fetch it with additional data
		"""
		key = gen_model_key(self.queryset.model, **kwargs)
		instance = cache.get(key, None)

		if not instance or instance.fetched_data:
			instance = self.get_object()
			instance.get_with_api_data(self.oauth_client)

		serializer = self.get_serializer(instance)
		return Response(serializer.data)
