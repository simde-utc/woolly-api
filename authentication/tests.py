from rest_framework.test import APITestCase
from rest_framework import status
from core.tests import CRUDViewSetTestMixin, get_permissions_from_compact

from authentication.models import *
from authentication.serializers import *
from faker import Faker
faker = Faker()


class UserViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = User
	permissions = get_permissions_from_compact({
		'list': 	"...a", 	# Only admin can list
		'retrieve': ".u.a", 	# Only user and admin can retrieve
		'create': 	"...a", 	# Only user and admin can create
		'update': 	".u.a", 	# Only user and admin can update
		'delete': 	"...a", 	# Only user and admin can delete
	})

	def _get_object_attributes(self, user=None):
		self.usertype = self.usertype or UserType.objects.create(name="Test_UserType")
		return {
			'email': faker.email(),
			'first_name': faker.first_name(),
			'last_name': faker.last_name(),
			'birthdate': faker.date_of_birth(),
			'usertype': self.usertype.pk
		}

	# Custom create to comply with the redirection
	def _create_object(self, user=None):
		return self.users['user']

	def test_create_view(self):
		url = self._get_url()
		self._test_user_permission(url, 'admin', method="post", data={}, expected_status_code=status.HTTP_302_FOUND)
		self._test_user_permission(url, 'user', method="post", data={}, expected_status_code=status.HTTP_403_FORBIDDEN)
		self._test_user_permission(url, 'public', method="post", data={}, expected_status_code=status.HTTP_403_FORBIDDEN)




class UserTypeViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = UserType
	permissions = get_permissions_from_compact({
		'list': 	"puoa", 	# Everyone can list
		'retrieve': "puoa", 	# Everyone can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	"...a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})

	def _get_object_attributes(self, user=None):
		return {
			'name': faker.sentence(nb_words=2),
		}
