from rest_framework.test import APITestCase
from rest_framework import status
from core.tests import FakeModelFactory, CRUDViewSetTestMixin, get_permissions_from_compact
from .models import *

modelFactory = FakeModelFactory()


# Used for Association, Sale, ItemGroup, Item, ItemField
ManagerOrReadOnly = get_permissions_from_compact({
	'list': 	"puoa", 	# Everyone can list
	'retrieve': "puoa", 	# Everyone can retrieve
	'create': 	"...a", 	# Only admin can create
	'update': 	"...a", 	# Only managers & admin can update
	'delete': 	"...a", 	# Only admin can delete
})

# Used for Order, OrderLine, OrderLineItem, OrderLineField
OrderOwnerOrAdmin = get_permissions_from_compact({
	'list': 	"...a", 	# Only admin can list
	'retrieve': ".u.a", 	# Only owner and admin can retrieve
	'create': 	".u.a", 	# Only owner and admin can create
	'update': 	".u.a", 	# Only owner and admin can update
	'delete': 	".u.a", 	# Only owner and admin can delete
})


class AssociationViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = Association
	permissions = ManagerOrReadOnly

"""
class AssociationMemberViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = AssociationMember
	permissions = get_permissions_from_compact({
		'list': 	"...a", 	# Only admin can list
		'retrieve': "...a", 	# Only admin can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	"...a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})
	def _get_object_attributes(self, user=None):
		return None
"""

# TODO check visibilities
class SaleViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = Sale
	permissions = ManagerOrReadOnly


class ItemGroupViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = ItemGroup
	permissions = ManagerOrReadOnly

# TODO test different usertypes
class ItemViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = Item
	permissions = ManagerOrReadOnly


class OrderViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = Order
	permissions = {
		**OrderOwnerOrAdmin,
		'create': ".uoa",		# Every logged user can create order
	}

class OrderLineViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = OrderLine
	permissions = OrderOwnerOrAdmin

	def _additionnal_setUp(self):
		self.sale = self.modelFactory.create(Sale)
		# Order is own by user for the purpose of the tests
		self.order = self.modelFactory.create(Order, owner=self.users['user'])
		self.assertEqual(self.order.owner, self.users['user'], "Erreur de configuration, l'order doit être faite par 'user'")

	def _get_object_attributes(self, user=None, withPk=True):
		overiddes = {
			'quantity': 5
		}
		return self.modelFactory.get_attributes(self.model, withPk=withPk, overiddes=overiddes, order=self.order)


class FieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = Field
	permissions = ManagerOrReadOnly

class ItemFieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = ItemField
	permissions = ManagerOrReadOnly


class OrderLineItemViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = OrderLineItem
	permissions = OrderOwnerOrAdmin

class OrderLineFieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = OrderLineField
	permissions = OrderOwnerOrAdmin
