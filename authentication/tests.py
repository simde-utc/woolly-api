from rest_framework.test import APITestCase
from rest_framework import status
from core.tests import CRUDViewSetTestMixin, get_permissions_from_compact
from authentication.models import *


class UserViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'user'
	permissions = get_permissions_from_compact({
		'list': 	"...a", 	# Only admin can list
		'retrieve': ".u.a", 	# Only user and admin can retrieve
		'create': 	"...a", 	# Only user and admin can create
		'update': 	".u.a", 	# Only user and admin can update
		'delete': 	"...a", 	# Only user and admin can delete
	})

	# Custom create to comply with the redirection
	def test_create_view(self):
		url = self._get_url()
		self._test_user_permission(url, 'admin', method="post", data={}, expected_status_code=status.HTTP_302_FOUND)
		self._test_user_permission(url, 'lambda1', method="post", data={}, expected_status_code=status.HTTP_403_FORBIDDEN)
		self._test_user_permission(url, None, method="post", data={}, expected_status_code=status.HTTP_403_FORBIDDEN)

	def _create_object(self, user=None):
		return self.users['user']



class UserTypeViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'usertype'
	permissions = get_permissions_from_compact({
		'list': 	"puoa", 	# Everyone can list
		'retrieve': "puoa", 	# Everyone can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	"...a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})

	def _create_object(self, user=None):
		return UserType.objects.create(name="Test_UserType")
