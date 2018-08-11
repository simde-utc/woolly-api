from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User


class CRUDViewSetTestMixin(object):
	resource_name = None
	route_visibility = {
		'public': False,
		'authenticated': False
	}

	def setUp(self):
		if self.resource_name is None:
			raise NotImplementedError("Please specify the resource_name")
		self.users = {
			'admin': User.objects.create_superuser(email="admin@woolly.com"),
			'lambda1': User.objects.create_user(email="lambda1@woolly.com"),
			'lambda2': User.objects.create_user(email="lambda2@woolly.com"),
		}

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
		self.assertEqual(response.status_code, expected_status_code, "for '%s' user" % user)

	def test_list_view(self):
		url = self._get_url()

		# Test List permissions
		self._test_user_permission(url, 'admin', True)
		self._test_user_permission(url, 'lambda1', self.route_visibility['authenticated'])
		self._test_user_permission(url, None, self.route_visibility['public'])


"""
class RoutesTestCase(CRUDViewSetTestMixin, APITestCase):

	def _test_one_route(self, route):
		self._get_url(route['name'])

		# Test List permissions
		self._test_user_permissions(url, 'admin', True)
		self._test_user_permissions(url, 'lambda1', not route['onlyAdmin'])
		self._test_user_permissions(url, None, route['public'])



def gen_route_test(route):
	return lambda self: self._test_one_route(route)
"""

ROUTE_LIST = [
	{ 'name': 'user', 				'public': False, 	'onlyAdmin': True },
	{ 'name': 'usertype', 			'public': True, 	'onlyAdmin': False },
	{ 'name': 'association', 		'public': True, 	'onlyAdmin': False },
	{ 'name': 'associationmember',	'public': False, 	'onlyAdmin': True },
	{ 'name': 'sale', 				'public': True, 	'onlyAdmin': False },
	{ 'name': 'itemgroup', 			'public': True, 	'onlyAdmin': False },
	{ 'name': 'item', 				'public': True, 	'onlyAdmin': False },
	{ 'name': 'order', 				'public': False, 	'onlyAdmin': True },
	{ 'name': 'orderline', 			'public': False, 	'onlyAdmin': True },
	{ 'name': 'orderlineitem', 		'public': False, 	'onlyAdmin': True },
	{ 'name': 'field', 				'public': True, 	'onlyAdmin': False },
	{ 'name': 'orderlinefield', 	'public': False, 	'onlyAdmin': True },
	{ 'name': 'itemfield', 			'public': True, 	'onlyAdmin': False },
]

# Programmaticaly add tests for each routes
# for route in ROUTE_LIST:
	# setattr(RoutesTestCase, 'test_'+route['name']+'_route', gen_route_test(route))
