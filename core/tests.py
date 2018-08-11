from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User
from copy import deepcopy

def debug_permissions(permissions):
	for action in permissions:
		string_list = (perm for perm in permissions[action] if permissions[action][perm] is True)
		print(action, ":\t\t" if len(action) < 6 else ":\t", ', '.join(string_list))

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

def get_permissions_from_compact(compact):
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
		if not self.resource_name:
			raise NotImplementedError("Please specify the resource_name")
		self.users = {
			'admin': User.objects.create_superuser(email="admin@woolly.com"),
			'lambda1': User.objects.create_user(email="lambda1@woolly.com"),
			'lambda2': User.objects.create_user(email="lambda2@woolly.com"),
		}
		if self.debug:
			print("\n")
			print("=" * (35 + len(self.resource_name)))
			print("    DEBUG: '"+self.resource_name+"' ViewTestCase")
			print("-" * (35 + len(self.resource_name)))
			debug_permissions(self.permissions)

	def _get_expected_permission(self, action, visibility):
		default = DEFAULT_CRUD_PERMISSIONS[action].get(visibility, False)
		return self.permissions[action].get(visibility, default)

	def _get_url(self, pk=None):
		try:
			if pk is None:
				return reverse(self.resource_name + '-list')
			else:
				return reverse(self.resource_name + '-detail', { 'pk': pk })
		except exceptions.NoReverseMatch:
			self.assertIsNotNone(url, "Route '%s' is not defined" % route['name'])

	def _test_user_permission(self, url, user = None, allowed = True):
		# Authenticate with specified user
		self.client.force_authenticate(user = self.users.get(user, None))

		# Get url and check code
		response = self.client.get(url, format='json')

		expected_status_code = status.HTTP_200_OK if allowed else status.HTTP_403_FORBIDDEN
		if self.debug:
			print(" Expected permission for '" + (user or 'public') +"': ", allowed)
		self.assertEqual(response.status_code, expected_status_code, "for '%s' user" % user)

	def test_list_view(self):
		url = self._get_url()
		if self.debug:
			print("\n== Begin '" + self.resource_name + "' list view test")
			print(" url:", url)

		# Test List permissions
		self._test_user_permission(url, 'admin', 	self._get_expected_permission('list', 'admin'))
		self._test_user_permission(url, 'lambda1', 	self._get_expected_permission('list', 'user'))
		self._test_user_permission(url, None, 		self._get_expected_permission('list', 'public'))

	def test_create_view(self):
		url = self._get_url()
		if self.debug:
			print("\n== Begin '" + self.resource_name + "' create view test")
			print(" url:", url)

		# Test List permissions
		self._test_user_permission(url, 'admin', 	self._get_expected_permission('list', 'admin'))
		self._test_user_permission(url, 'lambda1', 	self._get_expected_permission('list', 'user'))
		self._test_user_permission(url, None, 		self._get_expected_permission('list', 'public'))

