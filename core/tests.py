from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User
from copy import deepcopy
from rest_framework_json_api.renderers import JSONRenderer
from rest_framework_json_api.parsers import JSONParser


# Only admin can do things by default
DEFAULT_CRUD_PERMISSIONS = {
	'list': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'retrieve': { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'create': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'update': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'delete': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
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


class CRUDViewSetTestMixin(object):
	model = None
	permissions = DEFAULT_CRUD_PERMISSIONS
	debug = False

	def setUp(self):
		"""Function run before beginning the tests"""

		# resource_name MUST be specified
		if not self.model:
			raise NotImplementedError("Please specify the resource_name")

		self.resource_name = self.model.JSONAPIMeta.resource_name

		# Get users
		self.users = {
			'admin': User.objects.create_superuser(email="admin@woolly.com"),
			'user': User.objects.create_user(email="user@woolly.com"),
			'other': User.objects.create_user(email="other@woolly.com"),
			'public': None
		}

		# Create test object
		self.object = self._create_object(self.users.get('user'))

		# Additional setUp
		self._additionnal_setUp()

		# Debug
		if self.debug:
			print("\n")
			print("=" * (35 + len(self.resource_name)))
			print("    DEBUG: '"+self.resource_name+"' ViewTestCase")
			print("-" * (35 + len(self.resource_name)))
			debug_permissions(self.permissions)

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
		try:
			if pk is None:
				return reverse(self.resource_name + '-list')
			else:
				return reverse(self.resource_name + '-detail', kwargs={ 'pk': pk })
		except exceptions.NoReverseMatch:
			self.assertIsNotNone(url, "Route '%s' is not defined" % route['name'])

	def _get_expected_status_code(self, method, allowed):
		if not allowed:
			return status.HTTP_403_FORBIDDEN
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
		@param   user                  The user which does the request
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
		data = self._parse_data_for_request(data = kwargs.get('data', None), id = kwargs.get('id', None))
		call_method = getattr(self.client, HTTP_method)
		response = call_method(url, data, format='vnd.api+json')

		# Get expected status_code 
		expected_status_code = kwargs.get('expected_status_code', self._get_expected_status_code(HTTP_method, allowed))
		if self.debug:
			print(" Status code for '%s': \t expected %d, got %d" % ((user or 'public'), expected_status_code, response.status_code))

		# Build detailled error message
		error_message = "for '%s' user" % user
		if hasattr(response, 'data') and response.data:
			error_details = ', '.join(data.get('detail', '') for data in response.data if type(data) is dict)
			error_message += " (%s)" % error_details

		self.assertEqual(response.status_code, expected_status_code, error_message)


	def _create_object(self, user=None):
		"""Method used to create the initial object"""
		data = self._get_object_attributes(user)
		return self.model.objects.create(**data)

	def _get_object_attributes(self, user=None):
		"""Method used to create new object with user, must be overriden"""
		raise NotImplementedError("This function must be overriden")


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
		
		url = self._get_url(pk = options['id'])

		# Debug
		if self.debug:
			print("\n== Begin '%s' %s view test\n url : %s" % (self.resource_name, action, url))

		# Test permissions for all users
		for user in self.users:
			if action in ('create', 'update'):
				options['data'] = self._get_object_attributes(user)
				if self.debug:
					print(" options : ", options['data'])

			# Perform the test
			self._test_user_permission(url, user, self._is_allowed(action, user), **options)
			if action == 'update':			# Additionnal test with PUT for update
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

