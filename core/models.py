from django.db.utils import IntegrityError
from django.db.models import QuerySet, Model
from django.db.models.manager import BaseManager
from typing import Union, Sequence, Set, Tuple

from core.helpers import filter_dict_keys, iterable_to_map
from woolly_api.settings import API_MODEL_CACHE_TIMEOUT
from django.core.cache import cache
import logging

logger = logging.getLogger(f"woolly.{__name__}")


def fetch_data_from_api(model: 'Model', oauth_client: 'OAuthAPI'=None, **params):
	"""
	Fetched additional data from the OAuth API
	"""
	logger.debug(f"Fetching {model} from the API with params {params}")
	# Create a client if not given
	if oauth_client is None:
		from authentication.oauth import OAuthAPI
		oauth_client = OAuthAPI()

	# Fetch from the right resource URI and patch data if needed
	uri = model.get_api_endpoint(params)
	data = oauth_client.fetch_resource(uri)
	if hasattr(model, 'patch_fetched_data'):
		if type(data) is list:
			data = list(map(model.patch_fetched_data, data))
		else:
			data = model.patch_fetched_data(data)

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
		
	def get_with_api_data(self, oauth_client=None, single_result: bool=False, try_cache: bool=True, **params):
		"""
		Execute query and add extra data from the API
		"""
		# Set single_result automatically if only one result is expected
		if 'pk' in params and not hasattr(params['pk'], '__len__'):
			single_result = True

		# Try cache
		if try_cache:
			cached = self.model.get_from_cache(params, single_result=False, need_full_data=True)
			if cached is not None:
				return cached

		# Get database results, fetched data and some params
		field_names = self.model.field_names()
		fetched_data = self.fetch_api_data(oauth_client, **params)
		# TODO Fix potential errors
		can_filter = all(key in field_names for key in params)
		if can_filter:
			db_results = self.filter(**params)
			db_results = iterable_to_map(db_results, get_key=lambda obj: str(obj.id))
		else:
			db_results = {}

		# Iter through fetched data and extend results
		to_create = []
		to_update = []
		updated_fields = set()
		for data in fetched_data:
			obj = db_results.get(data['id'], None)

			# Object is not in database, create it and add it
			if obj is None:
				obj = self.model(**filter_dict_keys(data, field_names))
				obj.sync_data(data, save=False)
				to_create.append(obj)

			# Object exists, update it
			else:
				obj_updated_fields = obj.sync_data(data, save=False)
				if obj_updated_fields:
					to_update.append(obj)
					updated_fields |= obj_updated_fields

		# Create and update objects if needed
		if to_create:
			try:
				to_create = self.bulk_create(to_create)
				logger.debug(f"Created {len(to_create)} new {self.model.__class__.__name__}")
			except IntegrityError as error:
				# Some filtering may not work with the database even though the data
				# is already in the database so we simply skip trying to create
				# if we cannot be sure filtering went well
				if can_filter:
					raise error

		if to_update:
			self.bulk_update(to_update, updated_fields)

		# Cache and return list of models instance
		results = list(db_results.values()) + to_create
		if single_result:
			assert len(results) == 1
			results = results[0]
		
		self.model.save_to_cache(results, params)
		return results

class ApiManager(BaseManager.from_queryset(ApiQuerySet)):
	pass

class APIModel(Model):
	"""
	Model with additional data that can be fetched from the OAuth API
	"""
	objects = ApiManager()
	fetched_data = None
	CACHE_TIMEOUT = API_MODEL_CACHE_TIMEOUT

	@property
	def is_synched(self) -> bool:
		return bool(self.fetched_data)

	def __getattr__(self, attr: str):
		"""
		Try getting data from fetched_data if possible to act as a model field
		"""
		# try:
		# 	# Try getting real attribute first
		# 	return super().__getattr__(self, attr)
		# except AttributeError as error:
			# Then, search in fetched data
		if self.fetched_data and attr in self.fetched_data:
			return self.fetched_data[attr]
		raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{attr}'")

	@classmethod
	def field_names(cls) -> Tuple[str]:
		"""
		Get a list of the field names
		"""
		return tuple(field.name for field in cls._meta.fields)	

	@classmethod
	def get_api_endpoint(cls, params: dict) -> str:
		raise NotImplementedError("get_api_endpoint must be implemented")

	@classmethod
	def pk_to_url(cls, pk) -> str:
		if hasattr(pk, '__len__'):
			return f"/[{','.join(str(_pk) for _pk in pk)}]"
		else:
			return f"/{pk}" if pk else ''

	# ---------------------------------------------------------------------
	# 		Cache system
	# ---------------------------------------------------------------------

	@classmethod
	def _gen_key(cls, params: dict={}) -> str:
		"""
		Generate a key from a set of specifications
		"""
		name = cls.__name__.lower()
		spec = ','.join(f"{k}={v}" for k, v in params.items())
		return f"APIModel-{name}-{spec or 'all'}"

	@classmethod
	def get_from_cache(cls, params: dict, single_result: bool=False, need_full_data: bool=True) -> Union['APIModel', None]:
		"""
		Try getting model instance with fetched data from
		# TODO Improve for multiple queries
		"""
		key = cls._gen_key(params)
		if key in cache:
			return cache.get(key)

		# Try to get from cached -all
		if params:
			all_key = cls._gen_key()
			if all_key in cache:
				data = cache.get(all_key)

				# Find the right instances among all data
				results = []
				for instance in data:
					if all(getattr(instance, attr) == value for attr, value in params.items()):
						if need_full_data and not instance.fetched_data:
							logger.warning(f"Skipped cache because needed full data for {cls.__name__} with params {params}")
							return None

						if single_result:
							logger.debug(f"Got {cls.__name__} from cache with params {params}")
							return instance
						else:
							results.append(instance)

				if results:
					logger.debug(f"Got {cls.__name__} from cache with params {params}")
					return results

		return None

	@classmethod
	def save_to_cache(cls, data: Union[Sequence, 'APIModel'], params: dict):
		"""
		Save single or multiple instances to cache
		"""
		key = cls._gen_key(params)
		cache.set(key, data, cls.CACHE_TIMEOUT)
		logger.debug(f"Saved {len(data) if hasattr(data, '__len__') else 1} data with key={key}")

	@classmethod
	def remove_from_cache(cls, params: dict):
		key = cls._gen_key(params)
		if key in cache:
			# TODO WIP REMOVE
			return cache.get(key)


	# ---------------------------------------------------------------------
	# 		API Fetch and Sync methods
	# ---------------------------------------------------------------------

	fetch_api_data = classmethod(fetch_data_from_api)

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

	def get_with_api_data(self, oauth_client=None, save: bool=True, try_cache: bool=True):
		"""
		Get and sync additional data from OAuth API
		"""
		# Try cache
		if try_cache:
			cached = self.get_from_cache({ 'pk': self.pk }, single_result=True, need_full_data=True)
			if cached is not None:
				return cached

		# Else fetched and sync data
		self.sync_data(None, oauth_client, save=save)
		return self

	def save(self, *args, **kwargs):
		"""
		Override to update cache on save
		"""
		super().save(*args, **kwargs)
		self.save_to_cache(self, { 'pk': self.pk })

	class Meta:
		abstract = True
