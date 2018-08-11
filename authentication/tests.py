from rest_framework.test import APITestCase
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

class UserTypeViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'usertype'
	permissions = get_permissions_from_compact({
		'list': 	"puoa", 	# Everyone can list
		'retrieve': "puoa", 	# Everyone can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	"...a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})


