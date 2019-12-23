from core.testcases import ApiModelViewSetTestCase, ModelViewSetTestCase, get_permissions_from_compact
from rest_framework import status
from .models import *


class UserViewSetTestCase(ApiModelViewSetTestCase):
	model = User
	permissions = get_permissions_from_compact({
		'list':     '...a',    # Only admin can list
		'retrieve': '.u.a',    # Only user and admin can retrieve
		# 'update':   '.u.a',  # TODO Only user and admin can update ??
	})

	def create_object(self, user=None):
		return self.users['user']

class UserTypeViewSetTestCase(ModelViewSetTestCase):
	model = UserType
	permissions = get_permissions_from_compact({
		'list':     'puoa',    # Everyone can list
		'retrieve': 'puoa',    # Everyone can retrieve
		'create':   '...a',    # Only admin can create
		'update':   '...a',    # Only admin can update
		'delete':   '...a',    # Only admin can delete
	})
