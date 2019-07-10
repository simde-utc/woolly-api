from rest_framework import viewsets

class ModelViewSet(viewsets.ModelViewSet):

	def get_queryset(self):
		queryset = super().get_queryset()

		# Add include sub_models
		include_query = self.request.query_params.get('include')
		if include_query:
			queryset = queryset.prefetch_related(*include_query.split(','))

		# TODO Filter permission ??
		return queryset

	# def get_object(self):
	# 	return super().get_object()

	def get_serializer_context(self):
		include_query = self.request.query_params.get('include')
		return {
			**super().get_serializer_context(),
			'include_map': self.get_include_map(include_query),
		}

	@classmethod
	def get_include_map(self, include_query:str):
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


	# def filter_queryset(self, queryset):
	# 	return super().filter_queryset(queryset)

	# def handle_exception(self, exc):
	# 	"""Override from APIView"""
	# 	return super().handle_exception(exc)


