from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APITestCase
from authentication.models import User

def pp(obj):
	for prop in vars(obj):
		print(prop)#, '\t=> ', obj.get(prop, None))

class RoutesTestCase(APITestCase):
	def setUp(self):
		admin = User.objects.create_superuser(email="admin@woolly.com")
		self.client.force_authenticate(user=admin)

	def _test_one_route(self, route):
		try:
			url = reverse(route + '-list')
		except exceptions.NoReverseMatch:
			url = None
		self.assertIsNotNone(url, "Route '%s' is not defined" % route)

		response = self.client.get(url, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

def gen_route_test(route):
	return lambda self: self._test_one_route(route)

ROUTE_LIST = ['association', 'associationmember', 'sale', 'itemgroup', 'item',
	'order', 'orderline', 'orderlineitem', 'field', 'orderlinefield', 'itemfield']
# Programmaticaly add tests for each routes
for route in ROUTE_LIST:
	setattr(RoutesTestCase, 'test_'+route+'_route', gen_route_test(route))
