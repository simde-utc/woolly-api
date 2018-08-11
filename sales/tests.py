from rest_framework.test import APITestCase
from rest_framework import status
from core.tests import CRUDViewSetTestMixin, get_permissions_from_compact
from authentication.models import *

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
	resource_name = 'association'
	permissions = ManagerOrReadOnly


class AssociationMemberViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'associationmember'
	permissions = get_permissions_from_compact({
		'list': 	"...a", 	# Only admin can list
		'retrieve': "...a", 	# Only admin can retrieve
		'create': 	"...a", 	# Only admin can create
		'update': 	"...a", 	# Only admin can update
		'delete': 	"...a", 	# Only admin can delete
	})


class SaleViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'sale'
	permissions = ManagerOrReadOnly


class ItemGroupViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'itemgroup'
	permissions = ManagerOrReadOnly

class ItemViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'item'
	permissions = ManagerOrReadOnly


class OrderViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'order'
	permissions = OrderOwnerOrAdmin

class OrderLineViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'orderline'
	permissions = OrderOwnerOrAdmin


class FieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'field'
	permissions = ManagerOrReadOnly

class ItemFieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'itemfield'
	permissions = ManagerOrReadOnly


class OrderLineItemViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'orderlineitem'
	permissions = OrderOwnerOrAdmin

class OrderLineFieldViewSetTestCase(CRUDViewSetTestMixin, APITestCase):
	resource_name = 'orderlinefield'
	permissions = OrderOwnerOrAdmin
