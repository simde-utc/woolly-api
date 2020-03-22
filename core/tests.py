from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from core.helpers import get_model_name, pluralize

from copy import deepcopy
from .faker import FakeModelFactory

from authentication.models import *
from sales.models import *


# Only admin can do things by default
DEFAULT_CRUD_PERMISSIONS = {
	'list':     { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'retrieve': { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'create':   { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'update':   { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'delete':   { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
}

VISIBILITY_SHORTCUTS = {
	'p': 'public',
	'u': 'user',
	'o': 'other',
	'a': 'admin',
}


def debug_permissions(permissions):
	"""Helper to pretty print permissions"""
	for action in permissions:
		string_list = (perm for perm in permissions[action] if permissions[action][perm] is True)
		print(action, ":\t\t" if len(action) < 6 else ":\t", ', '.join(string_list))

def get_permissions_from_compact(compact):
	"""
	Helper to get a complete permission list from a compact one { 'list': "puoa", 'delete': ".u.a" }
	"""
	# Important ! https://www.peterbe.com/plog/be-careful-with-using-dict-to-create-a-copy
	permissions = deepcopy(DEFAULT_CRUD_PERMISSIONS)
	for action in compact:
		for letter in compact[action].replace('.', '').lower():
			visibility = VISIBILITY_SHORTCUTS[letter]
			permissions[action][visibility] = True
	return permissions

def format_date(date):
	return timezone.make_aware(date, timezone.get_current_timezone(), is_dst=False)


class CRUDViewSetTestMixin(object):
	model = None
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
		# try:
		if pk is None:
			return reverse(self.resource_name + '-list')
		else:
			return reverse(self.resource_name + '-detail', kwargs={ 'pk': pk })
		# except exceptions.NoReverseMatch:
		# 	self.assertIsNotNone(url, "Route '%s' is not defined" % route['name'])

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
		self.client.force_authenticate(user = self.users.get(user, None))

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


	def _perform_crud_test(self, action):
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


	# ========================================================
	# 		Tests
	# ========================================================

	def test_list_view(self):
		"""Test all users permissions to list"""
		self._perform_crud_test('list')

	def test_retrieve_view(self):
		"""Test all users permissions to retrieve self.object"""
		self._perform_crud_test('retrieve')

	def test_create_view(self):
		"""Test all users permissions to create an object"""
		self._perform_crud_test('create')

	def test_update_view(self):
		"""Test all users permissions to modify an object"""
		self._perform_crud_test('update')

	def test_delete_view(self):
		"""Test all users permissions to delete an object"""
		self._perform_crud_test('delete')

