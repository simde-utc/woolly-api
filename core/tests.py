from django.urls import reverse, exceptions
from rest_framework import status
from functools import partial
from copy import deepcopy
from typing import Dict

from rest_framework.test import APIClient
from contextlib import contextmanager
from django import db

from core.helpers import get_model_name, pluralize
from core.faker import FakeModelFactory
from authentication.models import User

PermissionList = Dict[str, Dict[str, bool]]

CRUD_ACTIONS = ('list', 'retrieve', 'create', 'update', 'delete')
# Only admin can do things by default
DEFAULT_CRUD_PERMISSIONS = {
	action: { 'public': False, 	'user': False, 	'other': False, 	'admin': True }
	for action in CRUD_ACTIONS
}
VISIBILITY_SHORTCUTS = {
	'p': 'public',
	'u': 'user',
	'o': 'other',
	'a': 'admin',
}


def debug_permissions(permissions: PermissionList):
	"""
	Helper to pretty print permissions
	"""
	for action, permission in permissions.items():
		string_list = (user for user, authorized in permission.items() if authorized is True)
		print(action, ":\t\t" if len(action) < 6 else ":\t", ', '.join(string_list))

def get_permissions_from_compact(compact: Dict[str, str]) -> PermissionList:
	"""
	Helper to get a complete permission list from a compact one { 'list': "puoa", 'delete': ".u.a" }
	"""
	# Important ! https://www.peterbe.com/plog/be-careful-with-using-dict-to-create-a-copy
	permissions = deepcopy(DEFAULT_CRUD_PERMISSIONS)
	for action, compact_str in compact.items():
		for letter in compact_str.replace('.', '').lower():
			visibility = VISIBILITY_SHORTCUTS[letter]
			permissions[action][visibility] = True
	return permissions

@contextmanager
def get_api_client(user: User=None) -> APIClient:
	"""
	Context manager to get an APIClient and clear connection if threaded
	
	Arguments:
		user (User): if specified login the APIClient with it (default: None)
	"""
	client = APIClient(enforce_csrf_checks=True)
	if user is not None:
		client.force_authenticate(user=user)
	try:
		yield client
	finally:
		db.connections.close_all()

class CRUDViewSetTestMeta(type):

	def __new__(metacls, name: str, bases: tuple, dct: dict):
		"""
		Attach CRUD test methods to the TestCase class 
		"""
		cls = super().__new__(metacls, name, bases, dct)
		if cls.model is None:
			return cls

		model_name = cls.model.__name__
		for action in cls.crud_actions:
			method_name = f"test_{action}_view"
			if not hasattr(cls, method_name):
				method = lambda self: self._perform_crud_test(action)
				method.__doc__ = f"Test all users permissions to {action} {model_name}"
				setattr(cls, method_name, method)

		return cls

class CRUDViewSetTestMixin(metaclass=CRUDViewSetTestMeta):
	model = None
	crud_actions = CRUD_ACTIONS
	permissions = DEFAULT_CRUD_PERMISSIONS
	modelFactory = FakeModelFactory()
	debug = False

	def setUp(self):
		"""Function run before beginning the tests"""
		if self.debug:
			print('')

		# Model MUST be specified
		if not self.model:
			raise ValueError("Please specify the model")

		self.resource_name = pluralize(get_model_name(self.model))

		# Get users
		self.users = {
			'admin':  self.modelFactory.create(User, email="admin@woolly.com", is_admin=True),
			'user':   self.modelFactory.create(User, email="user@woolly.com"),
			'other':  self.modelFactory.create(User, email="other@woolly.com"),
			'public': None
		}

		# Additional setUp
		self._additionnal_setUp()

		# Create test object
		self.object = self._create_object(self.users.get('user'))

		# Debug
		if self.debug:
			print("\n")
			print("=" * (35 + len(self.resource_name)))
			print("    DEBUG: '" + self.resource_name + "' ViewTestCase")
			print("-" * (35 + len(self.resource_name)))
			debug_permissions(self.permissions)
			print("Object :", self.object)

	def _additionnal_setUp(self):
		"""Method to be overriden in order to perform additional actions on setUp"""
		pass

	# ========================================================
	# 		Helpers
	# ========================================================

	def _is_allowed(self, action, visibility):
		"""Helper to know if action is allowed with specified visibility"""
		default = DEFAULT_CRUD_PERMISSIONS[action].get(visibility, False)
		return self.permissions[action].get(visibility, default)

	def _get_url(self, pk=None):
		"""Helper to get url from resource_name and pk"""
		if pk is None:
			return reverse(self.resource_name + '-list')
		else:
			return reverse(self.resource_name + '-detail', kwargs={ 'pk': pk })

	def _get_expected_status_code(self, method, allowed, user):
		if not allowed:
			return (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
		if method == 'post':
			return status.HTTP_201_CREATED
		if method == 'delete':
			return status.HTTP_204_NO_CONTENT
		return status.HTTP_200_OK

	def _parse_data_for_request(self, data, id=None):
		if data is None:
			return None
		return {
			'data': {
				'type': self.resource_name,
				'id': id,
				'attributes': data,
			}
		}

	def _test_user_permission(self, url, user=None, allowed=True, **kwargs):
		"""
		@brief   Helper to make the user try to access the url with specified method
		@param   url                   The url to access
		@param   user                  The user which does the request (BEWARE ! Actually the username key in self.users dict)
		@param   allowed               Whether the user should be allowed to perform the request
		@param   method                The HTTP method used to access the url
		@param   data                  The data to bind to the HTTP request
		@param   id                    The id of the resource to modify
		@param   expected_status_code  The status code that should be returned by the request
		"""
		# Authenticate with specified user
		self.client.force_authenticate(user=self.users.get(user, None))

		# Create request
		HTTP_method = kwargs.get('method', 'get')
		# data = self._parse_data_for_request(data=kwargs.get('data'), id=kwargs.get('id'))
		call_method = getattr(self.client, HTTP_method)
		response = call_method(url, kwargs.get('data'), format='json')

		# Get expected status_code 
		expected_status_code = kwargs.get('expected_status_code', self._get_expected_status_code(HTTP_method, allowed, user))
		if self.debug:
			print(" Status code for '%s': \t expected %d, got %d" % ((user or 'public'), expected_status_code, response.status_code))

		# Build detailled error message
		error_message = "for '%s' user" % user
		if hasattr(response, 'data') and response.data:
			# TODO Improve
			error_details = response.data.get('detail')
			error_message += " (%s)" % error_details
		assert_method = self.assertEqual if type(expected_status_code) is int else self.assertIn
		assert_method(response.status_code, expected_status_code, error_message)


	def _get_object_attributes(self, user=None, withPk=True):
		"""Method used to create new object with user, can be overriden"""
		return self.modelFactory.get_attributes(self.model, withPk=withPk, user=user)

	def _create_object(self, user=None):
		"""Method used to create the initial object, can be overriden"""
		data = self._get_object_attributes(user, withPk=False)
		return self.model.objects.create(**data)


	def _perform_crud_test(self, action: str):
		"""
		@brief   Helper to perform CRUD action tests
		@param   action           The url to access
		@param   withPkInUrl      Whether the url need a primary key or not
		"""

		action_to_method_map = {
			'list': 'get',
			'retrieve': 'get',			
			'create': 'post',
			'update': 'patch',
			'delete': 'delete',
		}

		# Build options
		options = dict()
		options['id'] = None if action in ('list', 'create') else self.object.pk
		options['method'] = action_to_method_map[action]
		
		url = self._get_url(pk=options['id'])

		# Debug
		if self.debug:
			print("\n== Begin '%s' %s view test\n url : %s" % (self.resource_name, action, url))

		# Test permissions for all users
		for user in self.users:
			# Re-save the object in the db in order to have the same after each user modifications
			self.object.save()

			if action in ('create', 'update'):
				options['data'] = self._get_object_attributes(self.users.get(user))
				if self.debug:
					print(" options : ", options['data'])

			# Perform the test
			self._test_user_permission(url, user, self._is_allowed(action, user), **options)

			# Additionnal test with PUT for update
			if action == 'update':
				options['method'] = 'put'
				self._test_user_permission(url, user, self._is_allowed(action, user), **options)
