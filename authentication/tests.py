from rest_framework.test import APITestCase
from core.tests import CRUDViewSetTestMixin
from authentication.models import *


class UserViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'user'
	route_visibility = {
		'public': False,
		'authenticated': False
	}

class UserTypeViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'usertype'
	route_visibility = {
		'public': True,
		'authenticated': True
	}

