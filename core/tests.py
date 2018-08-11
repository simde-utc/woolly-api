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
	resource_name = None
	permissions = DEFAULT_CRUD_PERMISSIONS
	debug = False

	def setUp(self):
		"""Function run before beginning the tests"""

		# resource_name MUST be specified
		if not self.resource_name:
			raise NotImplementedError("Please specify the resource_name")

		# Get users
		self.users = {
			'admin': User.objects.create_superuser(email="admin@woolly.com"),
			'user': User.objects.create_user(email="user@woolly.com"),
			'other': User.objects.create_user(email="other@woolly.com"),
			'public': None
		}

		# Create test object
		self.object = self._create_object()

		# Debug
		if self.debug:
			print("\n")
			print("=" * (35 + len(self.resource_name)))
			print("    DEBUG: '"+self.resource_name+"' ViewTestCase")
			print("-" * (35 + len(self.resource_name)))
			debug_permissions(self.permissions)

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
		return status.HTTP_200_OK

	def _parse_data_for_request(self, data, id=None):
		if data is None:
			return None
		return {
			'data': {
				'type': self.model.JSONAPIMeta.resource_name,
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
		@param   expected_status_code  The status code that should be returned by the request
		"""
		# Authenticate with specified user
		self.client.force_authenticate(user = self.users.get(user, None))

		# Create request
		HTTP_method = kwargs.get('method', 'get')
		data = self._parse_data_for_request(kwargs.get('data', None))
		call_method = getattr(self.client, HTTP_method)
		response = call_method(url, data, format='vnd.api+json')

		# Get expected status_code 
		expected_status_code = kwargs.get('expected_status_code', self._get_expected_status_code(HTTP_method, allowed))
		if self.debug:
			print(" Expected status_code for '" + (user or 'public') +"': ", expected_status_code)

		# Build detailled error message
		error_message = "for '%s' user" % user
		if hasattr(response, 'data'):
			error_details = ', '.join(data.get('detail', '') for data in response.data if type(data) is dict)
			error_message += " (%s)" % error_details

		self.assertEqual(response.status_code, expected_status_code, error_message)


	def _create_object(self, user=None):
		"""Method used to create the initial object with no user and then the per-user objects, must be overriden"""
		raise NotImplementedError("This function must be overriden")

	def _get_object_properties(self, user=None):
		"""Method used to create new object with user, must be overriden"""
		raise NotImplementedError("This function must be overriden")


	# ========================================================
	# 		Tests
	# ========================================================

	def test_list_view(self):
		"""Test all users permissions to list"""
		url = self._get_url()
		if self.debug:
			print("\n== Begin '" + self.resource_name + "' list view test")
			print(" url:", url)

		# Test permissions for all users
		for user in self.users:
			self._test_user_permission(url, user, self._is_allowed('list', user))

	def test_retrieve_view(self):
		"""Test all users permissions to retrieve self.object"""
		url = self._get_url(pk = self.object.pk)
		if self.debug:
			print("\n== Begin '" + self.resource_name + "' retrieve view test")
			print(" url:", url)

		# Test permissions for all users
		for user in self.users:
			self._test_user_permission(url, user, self._is_allowed('retrieve', user))

	def test_create_view(self):
		"""Test all users permissions to create an object"""
		url = self._get_url()
		if self.debug:
			print("\n== Begin '" + self.resource_name + "' create view test")
			print(" url:", url)

		# Test permissions for all users
		for user in self.users:
			data = self._get_object_properties(user)
			self._test_user_permission(url, user, self._is_allowed('create', user), method='post', data=data)

