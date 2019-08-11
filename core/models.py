from django.db.models import QuerySet, Model
from django.db.models.manager import BaseManager
from abc import abstractmethod
from typing import Set
from core.helpers import filter_dict_keys, iterable_to_map


def fetch_data_from_api(model, oauth_client=None, endpoint_params: dict={}):
	"""
	Fetched additional data from the API
	"""
	if oauth_client is None:
		from authentication.oauth import OAuthAPI
		oauth_client = OAuthAPI()

	uri = model.get_api_endpoint(**endpoint_params)
	data = oauth_client.fetch_resource(uri)
	if hasattr(model, 'patch_fetched_data'):
		return model.patch_fetched_data(data)
	return data


class ApiQuerySet(QuerySet):

	def fetch_api_data(self, oauth_client=None, endpoint_params: dict={}) -> list:
		"""
		Fetch data from the API
		"""
		if self.query.has_filters():
			# Return empty list if no results
			if not self:
				return []
	
			# Add pk specifications if filtered, else fetch all
			endpoint_params['pk'] = tuple(self.values_list('pk', flat=True))

		# Get database results, fetched data and some params
		return fetch_data_from_api(self.model, oauth_client, endpoint_params)
		
	def get_with_api_data(self, *args, **kwargs) -> list:
		"""
		Execute query and add extra data from the API
		"""
		# Return empty list if no results
		if self.query.has_filters() and not self:
			return []

		# Get database results, fetched data and some params
		fetched_data = self.fetch_api_data(*args, **kwargs)
		results = iterable_to_map(self, get_key=lambda obj: str(obj.id))
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

		# Return list of models instance
		return list(results.values()) + to_create
	
class ApiManager(BaseManager.from_queryset(ApiQuerySet)):
	pass

class ApiModel(Model):

	fetched_data = None
	fetch_api_data = classmethod(fetch_data_from_api)
	objects = ApiManager()

	@abstractmethod
	def get_api_endpoint(cls, **params) -> str:
		pass

	def sync_data(self, data: dict=None, oauth_client=None, save: bool=True) -> Set[str]:
		"""
		Update instance attributes with provided or fetched data
		"""
		# Fetch data if not provided
		if data is None:
			self.fetched_data = self.fetch_api_data(oauth_client, { 'pk': self.pk })
		else:
			self.fetched_data = data

		updated_fields = set()
		if self.id:
			# Update instance attributes
			for attr, value in self.fetched_data.items():
				# TODO
				if attr != 'id' and getattr(self, attr, '__NOT_THERE__') != value:
					if hasattr(self, attr):
						updated_fields.add(attr)
					setattr(self, attr, self.fetched_data[attr])

			# Save if required
			if updated_fields and save:
				self.save()

		return updated_fields

	def get_with_api_data(self, oauth_client=None):
		self.sync_data(None, oauth_client, save=True)
		return self


	@classmethod
	def field_names(cls):
		return tuple(field.name for field in cls._meta.fields)	

	class Meta:
		abstract = True
