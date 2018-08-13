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
		'create': { 'public': False, 'user': True, 'other': True, 'admin': True }, 	# Every logged user can create order
	}

	def _additionnal_setUp(self):
		self.sale = self.modelFactory.create(Sale)

	def _get_object_attributes(self, user=None, withPk=True):
		return self.modelFactory.get_attributes(self.model, withPk=withPk, sale=self.sale, owner=user)

	def _create_object(self, user=None):
		data = self._get_object_attributes(user, withPk=False)
		data['status'] = OrderStatus.NOT_PAID.value
		return self.model.objects.create(**data)

	def _get_expected_status_code(self, method, allowed, user):
		if not allowed:
			return status.HTTP_403_FORBIDDEN
		if method == 'post':
			return status.HTTP_200_OK if user == 'user' else status.HTTP_201_CREATED
		if method == 'delete':
			return status.HTTP_204_NO_CONTENT
		return status.HTTP_200_OK

class OrderLineViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = OrderLine
	permissions = OrderOwnerOrAdmin

	def _additionnal_setUp(self):
		# Order is own by user for the purpose of the tests
		self.order = self.modelFactory.create(Order, owner=self.users['user'])
		self.assertEqual(self.order.owner, self.users['user'], "Erreur de configuration, l'order doit être faite par 'user'")

	def _get_object_attributes(self, user=None, withPk=True):
		options = {
			'order': self.order,
			'quantity': 5
		}
		return self.modelFactory.get_attributes(self.model, withPk=withPk, **options)


class FieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = Field
	permissions = ManagerOrReadOnly

class ItemFieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = ItemField
	permissions = ManagerOrReadOnly


class OrderLineItemViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = OrderLineItem
	permissions = get_permissions_from_compact({
		'list': 	"...a", 	# Only admin can list
		'retrieve': ".u.a", 	# Only owner and admin can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	"...a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})

	def _additionnal_setUp(self):
		# Order is own by user for the purpose of the tests
		self.order = self.modelFactory.create(Order, owner=self.users['user'])
		self.orderline = self.modelFactory.create(OrderLine, order=self.order)
		self.assertEqual(self.orderline.order.owner, self.users['user'], "Erreur de configuration, l'order doit être faite par 'user'")

	def _get_object_attributes(self, user=None, withPk=True):
		return self.modelFactory.get_attributes(self.model, withPk=withPk, orderline=self.orderline)

class OrderLineFieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	model = OrderLineField
	permissions = get_permissions_from_compact({
		'list': 	"...a", 	# Only admin can list
		'retrieve': ".u.a", 	# Only owner and admin can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	".u.a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})

	def _additionnal_setUp(self):
		self.item = self.modelFactory.create(Item)
		self.field = self.modelFactory.create(Field)
		self.itemfield = self.modelFactory.create(ItemField, item=self.item, field=self.field, editable=True)

		# Order is own by user for the purpose of the tests
		self.order = self.modelFactory.create(Order, owner=self.users['user'])
		self.orderline = self.modelFactory.create(OrderLine, order=self.order, item=self.item, quantity=1)
		self.orderlineitem = self.modelFactory.create(OrderLineItem, orderline=self.orderline)

		# Tests
		self.assertEqual(self.orderlineitem.orderline.order.owner, self.users['user'])
		self.assertEqual(self.orderlineitem.orderline.item, self.item)
		self.assertEqual(self.itemfield.item, self.item)
		self.assertEqual(self.itemfield.field, self.field)

	def _get_object_attributes(self, user=None, withPk=True):
		options = {
			'orderlineitem': self.orderlineitem,
			'field': self.field,
		}
		return self.modelFactory.get_attributes(self.model, withPk=withPk, **options)
