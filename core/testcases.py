from typing import Any, Union, Sequence, Dict
from contextlib import contextmanager
from copy import deepcopy
from unittest.mock import patch

from django.urls import reverse
from django import db

from rest_framework import status
from rest_framework.test import APISimpleTestCase, APITestCase, APIClient

from core.helpers import get_model_name, pluralize
from core.faker import FakeModelFactory
from authentication.models import User


PermissionList = Dict[str, Dict[str, bool]]

CRUD_ACTIONS = ('list', 'retrieve', 'create', 'update', 'delete')
READ_ONLY_CRUD_ACTIONS = ('list', 'retrieve')

# Only admin can do things by default
DEFAULT_CRUD_PERMISSIONS = {
	action: { 'public': False, 'user': False, 'other': False, 'admin': True }
	for action in CRUD_ACTIONS
}
VISIBILITY_SHORTCUTS = {
	'p': 'public',
	'u': 'user',
	'o': 'other',
	'a': 'admin',
}
ACTION_TO_METHOD_MAP = {
	'list':     'get',
	'retrieve': 'get',
	'create':   'post',
	'update':   'patch',
	'delete':   'delete',
}


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
	"""
	Metaclass to attach CRUD test methods to the test class automatically

	You can disable this behavior with cls.auto_add_testcase=False
	or select the crud test methods with cls.crud_actions
	"""

	def __new__(metacls, name: str, bases: tuple, dct: dict):
		"""
		Attach CRUD test methods to the TestCase class
		"""
		# Add APITestCase to classes that implement a model but no TestCase
		auto_add_testcase = bool(dct.get('auto_add_testcase', True) and dct.get('model'))
		if auto_add_testcase and not any(issubclass(base, APISimpleTestCase) for base in bases):
			bases = bases + (APITestCase, )

		# Create class
		cls = super().__new__(metacls, name, bases, dct)
		if getattr(cls, 'model', None) is None:
			return cls

		# Attach missing CRUD methods if model implemented
		model_name = cls.model.__name__
		for action in cls.crud_actions:
			method_name = f"test_{action}_view"
			if not hasattr(cls, method_name):
				def method(self):
					return self._perform_crud_test(action)
				method.__doc__ = f"Test users permissions to {action} {model_name}"
				setattr(cls, method_name, method)

		return cls

class CRUDTestCaseMixin:
	"""
	TestCase mixin specialised in testing CRUD ModelViewSet
	regarding to the specified model

	First the setUp method is used to create users and the object.
	You can add custom setup by overloading additionnal_setUp or create_object.
	The entry point for testing is _perform_crud_test.

	Variables:
		model: the model linked to the ModemViewSet to test
		crud_actions (tuple): the CRUD actions to test automatically
		permissions (PermissionList): the different users permissions on different CRUD actions
		modelFactory (FakeModelFactory): a fake model factory to create objects
		auto_add_testcase (bool): whether to automatically add a APITestCase as base if none implemented
	"""

	model = None
	crud_actions = None
	permissions = DEFAULT_CRUD_PERMISSIONS
	modelFactory = FakeModelFactory()
	auto_add_testcase = True

	def setUp(self) -> None:
		"""
		Create users and object required to perform tests
		"""
		# model MUST be specified
		if not self.model:
			raise ValueError("Please specify the model")

		# Create test users users
		self.users = {
			'admin':  self.modelFactory.create(User, email="admin@woolly.com", is_admin=True),
			'user':   self.modelFactory.create(User, email="user@woolly.com"),
			'other':  self.modelFactory.create(User, email="other@woolly.com"),
			'public': None
		}

		# Run additional setUp if needed
		self.additionnal_setUp()

		# Create test object
		self.resource_name = pluralize(get_model_name(self.model))
		self.object = self.create_object(self.users.get('user'))

	def additionnal_setUp(self) -> None:
		"""
		Method that can be overriden in order to perform additional actions on setUp.
		Usually used to create related data. Run just after users creation.
		"""
		pass

	# ========================================================
	# 		Helpers
	# ========================================================

	def create_object(self, user: User=None):
		"""
		Method used to create the initial object on setUp, can be overriden
		"""
		data = self.get_object_attributes(user, withPk=False)
		return self.model.objects.create(**data)

	def get_url(self, pk: Any=None) -> str:
		"""
		Helper to get url from resource_name and pk
		"""
		if pk is None:
			return reverse(self.resource_name + '-list')
		else:
			return reverse(self.resource_name + '-detail', kwargs={ 'pk': pk })

	def is_allowed(self, action: str, visibility: str) -> bool:
		"""Helper to know if action is allowed with specified visibility

		Args:
			action (str): the CRUD action
			visibility (str): the user visibility

		Returns:
			bool: whether the user is allowed to perform the action or not
		"""
		default = DEFAULT_CRUD_PERMISSIONS[action].get(visibility, False)
		return self.permissions[action].get(visibility, default)

	def get_expected_status_code(self, method: str, allowed: bool, user: str) -> Union[int, Sequence[int]]:
		"""
		Get the HTTP status that is expected for a certain request

		Args:
			method (str): the HTTP method
			allowed (bool): whether the action should be allowed or not
			user (str): the user key that performs the action

		Returns:
			Union[int, Sequence[int]]: one or multiple expected status codes
		"""
		if not allowed:
			return (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
		if method == 'post':
			return status.HTTP_201_CREATED
		if method == 'delete':
			return status.HTTP_204_NO_CONTENT
		return status.HTTP_200_OK

	def get_object_attributes(self, user: User=None, withPk: bool=True) -> dict:
		"""
		Method used to generate new object data with user, can be overriden

		Args:
			user: the User attached to the object (default: None)
			withPk:  (default: True)

		Returns:
			dict: the generated data for the object
		"""
		return self.modelFactory.get_attributes(self.model, withPk=withPk, user=user)

	# ========================================================
	# 		Test methods
	# ========================================================

	def _test_user_permission(self, url: str, user: str=None, allowed: bool=False,
	                          method: str='get', data: dict=None, expected_status_code: int=None):
		"""
		Helper to make the user try to request the url with specified method

		Args:
			url (str):                   The url to access
			user (str):                  The user key which does the request (default: None)
			allowed (bool):              Whether the user should be allowed to perform the request (default: True)
			method (str):                The HTTP method used to access the url (default: 'get')
			data (dict):                 The data to bind to the HTTP request (default: None)
			expected_status_code (int):  The status code that should be returned by the request
		"""
		# Authenticate with specified user and request resource
		self.client.force_authenticate(user=self.users.get(user, None))
		request_method = getattr(self.client, method)
		response = request_method(url, data, format='json')

		# Get expected status_code if needed
		if expected_status_code is None:
			expected_status_code = self.get_expected_status_code(method, allowed, user)

		# Build detailled error message
		# TODO Improve with general ErrorResponse
		error_message = f"for user '{user}'"
		if getattr(response, 'data', None):
			error_message += f"\nErrorDetails: {response.data}"

		# Assert that we get the right status_code
		assert_method = self.assertEqual if type(expected_status_code) is int else self.assertIn
		assert_method(response.status_code, expected_status_code, error_message)
		# TODO Improve tests

	def _perform_crud_test(self, action: str):
		"""
		Method to perform CRUD action tests for all users

		It makes an API call to the model's and action's related url
		with all 4 different users and check if the response is as expected.

		Args:
			action: the CRUD action to perform
		"""
		# Build url and base test options
		url = self.get_url(pk=(None if action in ('list', 'create') else self.object.pk))
		options = {
			'method': ACTION_TO_METHOD_MAP[action]
		}

		# Test permissions for all users
		# Patch OAuthAPI.fetch_resource
		with patch('authentication.oauth.OAuthAPI.fetch_resource'):
			for user in self.users:
				with self.subTest(user=user):
					# Re-save the object in the db in order to have the same after each user modifications
					self.object.save()

					is_allowed = self.is_allowed(action, user)
					if action in ('create', 'update'):
						options['data'] = self.get_object_attributes(self.users.get(user))
					else:
						options['data'] = None

					# Perform the test
					self._test_user_permission(url, user, is_allowed, **options)

					# Additionnal test with PUT for update
					if action == 'update':
						options['method'] = 'put'
						self._test_user_permission(url, user, is_allowed, **options)


class ModelViewSetTestCase(CRUDTestCaseMixin, metaclass=CRUDViewSetTestMeta):
	"""
	Implementation of CRUD TestCase for full ModelViewSet
	"""
	crud_actions = CRUD_ACTIONS

class APIModelViewSetTestCase(CRUDTestCaseMixin, metaclass=CRUDViewSetTestMeta):
	"""
	Implementation of CRUD TestCase for APIModelViewSet
	"""
	crud_actions = READ_ONLY_CRUD_ACTIONS

	def _test_not_allowed_method(self, method: str, withPk: bool=False):
		url = self.get_url(pk=(self.object.pk if withPk else None))
		for user in self.users:
			codes = (status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED)
			self._test_user_permission(url, user, method=method, expected_status_code=codes)

	def test_create_view(self):
		"""
		Test that it is not possible to create a resource through the API
		"""
		self._test_not_allowed_method('post')

	def test_update_view(self):
		"""
		Test that it is not possible to update a resource through the API
		"""
		self._test_not_allowed_method('put', withPk=True)
		self._test_not_allowed_method('patch', withPk=True)

	def test_delete_view(self):
		"""
		Test that it is not possible to delete a resource through the API
		"""
		self._test_not_allowed_method('delete', withPk=True)
