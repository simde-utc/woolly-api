from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User


class RoutesTestCase(APITestCase):
	def setUp(self):
		self.users = {
			'admin': User.objects.create_superuser(email="admin@woolly.com"),
			'lambda1': User.objects.create_user(email="lambda1@woolly.com"),
			'lambda2': User.objects.create_user(email="lambda2@woolly.com"),
		}

	def _test_user_permissions(self, url, user = None, allowed = True):
		# Authenticate with specified user
		self.client.force_authenticate(user = self.users.get(user, None))
		# Get url and check code
		response = self.client.get(url, format='json')

		status_code = status.HTTP_200_OK if allowed else status.HTTP_403_FORBIDDEN
		# status_code = status.HTTP_401_UNAUTHORIZED if user is None else status.HTTP_403_FORBIDDEN

		error_msg = "is allowed" if response.status_code == status.HTTP_200_OK else "is not allowed"
		self.assertEqual(response.status_code, status_code, "'%s' user %s, but it should not" % (user, error_msg))
		

	def _test_one_route(self, route):
		try:
			url = reverse(route['name'] + '-list')
		except exceptions.NoReverseMatch:
			url = None
		self.assertIsNotNone(url, "Route '%s' is not defined" % route['name'])

		# Test List permissions
		self._test_user_permissions(url, 'admin', True)
		self._test_user_permissions(url, 'lambda1', not route['onlyAdmin'])
		self._test_user_permissions(url, None, route['public'])



def gen_route_test(route):
	return lambda self: self._test_one_route(route)

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
for route in ROUTE_LIST:
	setattr(RoutesTestCase, 'test_'+route['name']+'_route', gen_route_test(route))
