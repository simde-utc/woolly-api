from rest_framework import viewsets

class ModelViewSet(viewsets.ModelViewSet):

	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	# 	print("-- ModelViewSet.__init__ -- ", self.__class__.__name__)

	def get_queryset(self):
		queryset = super().get_queryset()

		# Add include sub_models
		include_query = self.request.query_params.get('include')
		if include_query:
			import pdb; pdb.set_trace()
			queryset = queryset.prefetch_related(include_query)

		# Filter permission ??
		return queryset

	# def get_object(self):
	# 	return super().get_object()

	# def get_serializer(self, *args, **kwargs):
	# 	"""Override of GenericAPIView.get_serializer"""
	# 	# self.include_map
	# 	return super().get_serializer(*args, **kwargs)

	# def get_serializer_class(self):
	# 	return super().get_serializer_class()

	def get_serializer_context(self):
		return {
			**super().get_serializer_context(),
			'include_map': self.get_include_map(),
		}

	def get_include_map(self):
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
		include_query = self.request.query_params.get('include')
		if not include_query:
			return None

		include_map = {}
		for path in include_query.split(','):
			current_map = include_map
			for step in path.split('__'):
				if step not in current_map:
					current_map[step] = {}
				current_map = current_map[step]

		import pdb; pdb.set_trace()

		return include_map



	# def filter_queryset(self, queryset):
	# 	return super().filter_queryset(queryset)

	# def handle_exception(self, exc):
	# 	"""Override from APIView"""
	# 	return super().handle_exception(exc)


