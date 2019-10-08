from django.db.models import QuerySet, Model
from django.db.models.manager import BaseManager
from core.helpers import filter_dict_keys, iterable_to_map
from django.core.cache import cache
from abc import abstractmethod
from typing import Set, Tuple

API_MODEL_CACHE_TIMEOUT = 3600

def gen_model_key(model_class: str, *args, **kwargs) -> str:
	"""
	Generate a key for a model from a set of specifications
	"""
	name = model_class.__name__.lower()
	spec = ','.join(f"{k}={v}" for k, v in kwargs.items())
	return f"model-{name}-{spec or 'all'}"

def fetch_data_from_api(model, oauth_client=None, **params):
	"""
	Fetched additional data from the OAuth API
	"""
	# Create a client if not given
	if oauth_client is None:
		from authentication.oauth import OAuthAPI
		oauth_client = OAuthAPI()

	# Fetch from the right resource URI and patch data if needed
	uri = model.get_api_endpoint(**params)
	data = oauth_client.fetch_resource(uri)
	if hasattr(model, 'patch_fetched_data'):
		return model.patch_fetched_data(data)

	return data


class ApiQuerySet(QuerySet):
	"""
	QuerySet that can also fetch additional data from the OAuth API
	"""

	def fetch_api_data(self, oauth_client=None, **params) -> list:
		"""
		Fetch data from the OAuth API
		"""
		if self.query.has_filters():
			# Return empty list if no results
			if not self:
				return []
	
			# Add pk specifications if filtered, else fetch all
			params['pk'] = tuple(self.values_list('pk', flat=True))

		# Fetch data
		return fetch_data_from_api(self.model, oauth_client, **params)
		
	def get_with_api_data(self, oauth_client=None, single_result: bool=False, **params):
		"""
		Execute query and add extra data from the API
		"""
		# Set single_result automatically if only one result is expected
		if 'pk' in params and not hasattr(params['pk'], '__len__'):
			single_result = True

		# Try cache
		key = gen_model_key(self.model, **params)
		results = cache.get(key, None)
		if results is not None:
			return results

		# Get database results, fetched data and some params
		clone = self.filter(**params)
		# TODO Fix potential errors
		results = iterable_to_map(clone, get_key=lambda obj: str(obj.id))
		fetched_data = self.fetch_api_data(oauth_client, **params)
		field_names = self.model.field_names()

		# Iter through fetched data and extend results
		to_create = []
		to_update = []
		updated_fields = set()
		for _data in fetched_data:
			obj = results.get(_data['id'], None)

			# Object is not in database, create it and add it
			if obj is None:
				obj = self.model(**filter_dict_keys(_data, field_names))
				to_create.append(obj)

			# Object exists, update it
			else:
				obj_updated_fields = obj.sync_data(_data, save=False)
				if obj_updated_fields:
					to_update.append(obj)
					updated_fields |= obj_updated_fields

		# Create and update objects if needed
		if to_create:
			to_create = self.bulk_create(to_create)
		if to_update:
			self.bulk_update(to_update, updated_fields)

		# Cache and return list of models instance
		results = list(results.values()) + to_create
		if single_result:
			assert len(results) == 1
			results = results[0]
		
		cache.set(key, results, API_MODEL_CACHE_TIMEOUT)
		return results


class ApiManager(BaseManager.from_queryset(ApiQuerySet)):
	pass

class ApiModel(Model):
	"""
	Model with additional data that can be fetched from the OAuth API
	"""
	objects = ApiManager()
	fetched_data = None
	fetch_api_data = classmethod(fetch_data_from_api)

	def __getattr__(self, attr):
		"""
		Try getting data from fetched_data if possible to act as a model field
		"""
		try:
			# Try getting real attribute first
			return super().__getattr__(self, attr)
		except AttributeError as error:
			# Then, search in fetched data
			if self.fetched_data and attr in self.fetched_data:
				return self.fetched_data[attr]
			raise error

	@classmethod
	def get_api_endpoint(cls, **params) -> str:
		raise NotImplementedError("get_api_endpoint must be implemented")

	@classmethod
	def pk_to_url(cls, pk) -> str:
		if hasattr(pk, '__len__'):
			return f"/[{','.join(str(_pk) for _pk in pk)}]"
		else:
			return f"/{pk}" if pk else ''

	def sync_data(self, data: dict=None, oauth_client=None, save: bool=True) -> Set[str]:
		"""
		Update instance attributes with patched provided or fetched data
		"""
		# Fetch data if not provided, patch and link
		if data is None:
			data = self.fetch_api_data(oauth_client, pk=self.pk)
		self.fetched_data = data

		# Update fields attributes
		updated_fields = set()
		for attr in self.field_names():
			if attr != 'id' and attr in self.fetched_data:
				value = self.fetched_data[attr]
				if getattr(self, attr) != value:
					setattr(self, attr, value)
					updated_fields.add(attr)

		# Save if required
		if save and updated_fields:
			self.save()

		return updated_fields

	def get_with_api_data(self, oauth_client=None, save: bool=True):
		"""
		Get and sync additional data from OAuth API
		"""
		# Try cache
		key = gen_model_key(type(self), pk=self.pk)
		cached = cache.get(key, None)
		if cached is not None:
			return cached

		# Else fetched and sync data
		self.sync_data(None, oauth_client, save=save)
		return self

	def save(self, *args, **kwargs):
		"""
		Override to update cache on save
		"""
		result = super().save(*args, **kwargs)
		key = gen_model_key(type(self), pk=self.pk)
		cache.set(key, self, API_MODEL_CACHE_TIMEOUT)
		return result

	@classmethod
	def field_names(cls) -> Tuple[str]:
		"""
		Get a list of the field names
		"""
		return tuple(field.name for field in cls._meta.fields)	

	class Meta:
		abstract = True
