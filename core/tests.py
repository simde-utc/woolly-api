from django.urls import reverse, exceptions
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from copy import deepcopy
from faker import Faker

from authentication.models import *
from sales.models import *


# Only admin can do things by default
DEFAULT_CRUD_PERMISSIONS = {
	'list': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'retrieve': { 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'create': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'update': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
	'delete': 	{ 'public': False, 	'user': False, 	'other': False, 	'admin': True },
}

VISIBILITY_SHORTCUTS = {
	'p': 'public',
	'u': 'user',
	'o': 'other',
	'a': 'admin',
}


def debug_permissions(permissions):
	"""Helper to pretty print permissions"""
	for action in permissions:
		string_list = (perm for perm in permissions[action] if permissions[action][perm] is True)
		print(action, ":\t\t" if len(action) < 6 else ":\t", ', '.join(string_list))

def get_permissions_from_compact(compact):
	"""
	Helper to get a complete permission list from a compact one { 'list': "puoa", 'delete': ".u.a" }
	"""
	# Important ! https://www.peterbe.com/plog/be-careful-with-using-dict-to-create-a-copy
	permissions = deepcopy(DEFAULT_CRUD_PERMISSIONS)
	for action in compact:
		for letter in compact[action].replace('.', '').lower():
			visibility = VISIBILITY_SHORTCUTS[letter]
			permissions[action][visibility] = True
	return permissions

def format_date(date):
	return timezone.make_aware(date, timezone.get_current_timezone(), is_dst=False)

class FakeModelFactory(object):

	def __init__(self, seed=None):
		self.faker = Faker()
		if seed:
			self.faker.seed(seed)

	def create(self, model, nb=None, **kwargs):
		if nb is None:
			props = self.get_attributes(model, **kwargs)
			return model.objects.create(**props)

		fake_models = list()
		for i in range(nb):
			props = self.get_attributes(model, **kwargs)
			fake_models.append(model.objects.create(**props))
		return fake_models

	def get_attributes(self, model, withPk=False, **kwargs):

		def _get_related(kw, model):
			related = kwargs.get(kw, self.create(model))
			jsonApiId = {
				'type': model.JSONAPIMeta.resource_name,
				'id': 	related.pk if hasattr(related, 'pk') else None,
			}
			return jsonApiId if withPk else related

		# ============================================
		# 	Authentication
		# ============================================

		if model == User:
			return {
				'email': 		kwargs.get('email', 		self.faker.email()),
				'first_name': 	kwargs.get('first_name', 	self.faker.first_name()),
				'last_name': 	kwargs.get('last_name', 	self.faker.last_name()),
				# 'birthdate': 	kwargs.get('birthdate', 	self.faker.date_of_birth()),
				'usertype': 	kwargs.get('usertype', 		_get_related('usertype', UserType))
			}

		if model == UserType:
			return {
				'name': kwargs.get('name', self.faker.sentence(nb_words=4)),
			}

		# ============================================
		# 	Association & Sale
		# ============================================

		if model == Association:
			return {
				'name':		kwargs.get('name', 		self.faker.company()),
				'fun_id':	kwargs.get('fun_id', 	self.faker.random_number()),
			}

		# if model == AssociationMember:
	
		if model == Sale:
			return {
				'name':			kwargs.get('name',			self.faker.company()),
				'description': 	kwargs.get('description',	self.faker.paragraph()),
				'association': 	_get_related('association', Association),
				'is_active': 	kwargs.get('is_active', True),
				'public': 		kwargs.get('public', 	True),
				'begin_at':		format_date(kwargs.get('begin_at',
						self.faker.date_time_this_year(before_now=True, after_now=False
				))),
				'end_at': 		format_date(kwargs.get('end_at',
						self.faker.date_time_this_year(before_now=False, after_now=True
				))),
				'max_item_quantity': kwargs.get('max_item_quantity', self.faker.random_number()),
				'max_payment_date':	 format_date(kwargs.get('max_payment_date',
					self.faker.date_time_this_year(before_now=False, after_now=True
				))),
			}

		# ============================================
		# 	Item & ItemGroup
		# ============================================

		if model == ItemGroup:
			return {
				'name': 		kwargs.get('name',			self.faker.word()),
				'quantity': 	kwargs.get('quantity',		self.faker.random_number()),
				'max_per_user': kwargs.get('max_per_user',	self.faker.random_number()),
			}

		if model == Item:
			return {
				'name': 		kwargs.get('name', self.faker.word()),
				'description': 	kwargs.get('description', self.faker.paragraph()),
				'sale':			_get_related('sale', Sale),
				'group':		_get_related('group', ItemGroup),
				'usertype': 	_get_related('usertype', UserType),
				'quantity': 	kwargs.get('quantity', 		self.faker.random_number()),
				'max_per_user': kwargs.get('max_per_user', 	self.faker.random_number()),
				'is_active': 	kwargs.get('is_active', 	True),
				'quantity': 	kwargs.get('quantity', 		self.faker.random_number()),
				'price': 		float(kwargs.get('price', 	self.faker.random_number()/10.)),
				'nemopay_id': 	kwargs.get('nemopay_id', 	self.faker.random_number()),
				'max_per_user': kwargs.get('max_per_user', 	self.faker.random_number()),
				# 'fields':
			}

		# ============================================
		# 	Order, OrderLine, OrderLineItem
		# ============================================

		if model == Order:
			return {
				'owner':		_get_related('owner', User),
				'sale':			_get_related('sale', Sale),
				'created_at':	format_date(kwargs.get('created_at', 
					self.faker.date_time_this_year(before_now=True, after_now=False
				))),
				'updated_at':	format_date(kwargs.get('updated_at', 
					self.faker.date_time_this_year(before_now=True, after_now=False
				))),
				'status':		kwargs.get('status', OrderStatus.ONGOING.value),
				'tra_id':		kwargs.get('tra_id', self.faker.random_number()),
			}

		if model == OrderLine:
			return {
				'item': 	_get_related('item', Item),
				'order': 	_get_related('order', Order),
				'quantity': kwargs.get('quantity', self.faker.random_digit()),
			}

		if model == OrderLineItem:
			return {
				'orderline': _get_related('orderline', OrderLine),
			}

		# ============================================
		# 	Field, ItemField, OrderLineField
		# ============================================

		if model == Field:
			return {
				'name': 	kwargs.get('name', 		self.faker.word()),
				'type': 	kwargs.get('type', 		self.faker.word()),
				'default': 	kwargs.get('default', 	self.faker.word()),
				# 'items': 	
			}

		if model == ItemField:
			return {
				'field': 	_get_related('field', Field),
				'item': 	_get_related('item', Item),
				'editable': kwargs.get('editable', self.faker.boolean()),
			}

		if model == OrderLineField:
			return {
				'orderlineitem': _get_related('orderlineitem', OrderLineItem),
				'field': 		 _get_related('field', Field),
				'value': 		 kwargs.get('value', self.faker.word()),
			}

		raise NotImplementedError("This model isn't faked yet")


class CRUDViewSetTestMixin(object):
	model = None
	permissions = DEFAULT_CRUD_PERMISSIONS
	modelFactory = FakeModelFactory()
	debug = False

	def setUp(self):
		"""Function run before beginning the tests"""
		if self.debug:
			print('')

		# resource_name MUST be specified
		if not self.model:
			raise NotImplementedError("Please specify the model")

		self.resource_name = self.model.JSONAPIMeta.resource_name

		# Get users
		self.users = {
			'admin':  User.objects.create_superuser(email="admin@woolly.com"),
			'user':   User.objects.create_user(email="user@woolly.com"),
			'other':  User.objects.create_user(email="other@woolly.com"),
			'public': None
		}

		# Additional setUp
		self._additionnal_setUp()

		# Create test object
		self.object = self._create_object(self.users.get('user'))

		# Debug
		if self.debug:
			print("\n")
			print("=" * (35 + len(self.resource_name)))
			print("    DEBUG: '" + self.resource_name + "' ViewTestCase")
			print("-" * (35 + len(self.resource_name)))
			debug_permissions(self.permissions)
			print("Object :", self.object)

	def _additionnal_setUp(self):
		"""Method to be overriden in order to perform additional actions on setUp"""
		pass

	# ========================================================
	# 		Helpers
	# ========================================================

	def _is_allowed(self, action, visibility):
		"""Helper to know if action is allowed with specified visibility"""
		default = DEFAULT_CRUD_PERMISSIONS[action].get(visibility, False)
		return self.permissions[action].get(visibility, default)

	def _get_url(self, pk=None):
		"""Helper to get url from resource_name and pk"""
		try:
			if pk is None:
				return reverse(self.resource_name + '-list')
			else:
				return reverse(self.resource_name + '-detail', kwargs={ 'pk': pk })
		except exceptions.NoReverseMatch:
			self.assertIsNotNone(url, "Route '%s' is not defined" % route['name'])

	def _get_expected_status_code(self, method, allowed, user):
		if not allowed:
			return status.HTTP_403_FORBIDDEN
		if method == 'post':
			return status.HTTP_201_CREATED
		if method == 'delete':
			return status.HTTP_204_NO_CONTENT
		return status.HTTP_200_OK

	def _parse_data_for_request(self, data, id=None):
		if data is None:
			return None
		return {
			'data': {
				'type': self.resource_name,
				'id': id,
				'attributes': data,
			}
		}

	def _test_user_permission(self, url, user=None, allowed=True, **kwargs):
		"""
		@brief   Helper to make the user try to access the url with specified method
		@param   url                   The url to access
		@param   user                  The user which does the request (BEWARE ! Actually the username key in self.users dict)
		@param   allowed               Whether the user should be allowed to perform the request
		@param   method                The HTTP method used to access the url
		@param   data                  The data to bind to the HTTP request
		@param   id                    The id of the resource to modify
		@param   expected_status_code  The status code that should be returned by the request
		"""
		# Authenticate with specified user
		self.client.force_authenticate(user = self.users.get(user, None))

		# Create request
		HTTP_method = kwargs.get('method', 'get')
		data = self._parse_data_for_request(data = kwargs.get('data', None), id = kwargs.get('id', None))
		call_method = getattr(self.client, HTTP_method)
		response = call_method(url, data, format='vnd.api+json')

		# Get expected status_code 
		expected_status_code = kwargs.get('expected_status_code', self._get_expected_status_code(HTTP_method, allowed, user))
		if self.debug:
			print(" Status code for '%s': \t expected %d, got %d" % ((user or 'public'), expected_status_code, response.status_code))

		# Build detailled error message
		error_message = "for '%s' user" % user
		if hasattr(response, 'data') and response.data:
			error_details = ', '.join(
				data.get('detail', '') + " [%s]" % data['source']['pointer'] \
				for data in response.data if type(data) is dict
			)
			error_message += " (%s)" % error_details
		self.assertEqual(response.status_code, expected_status_code, error_message)


	def _get_object_attributes(self, user=None, withPk=True):
		"""Method used to create new object with user, can be overriden"""
		return self.modelFactory.get_attributes(self.model, withPk=withPk, user=user)

	def _create_object(self, user=None):
		"""Method used to create the initial object, can be overriden"""
		data = self._get_object_attributes(user, withPk=False)
		return self.model.objects.create(**data)


	def _perform_crud_test(self, action):
		"""
		@brief   Helper to perform CRUD action tests
		@param   action           The url to access
		@param   withPkInUrl      Whether the url need a primary key or not
		"""

		action_to_method_map = {
			'list': 'get',
			'retrieve': 'get',			
			'create': 'post',
			'update': 'patch',
			'delete': 'delete',
		}

		# Build options
		options = dict()
		options['id'] = None if action in ('list', 'create') else self.object.pk
		options['method'] = action_to_method_map[action]
		
		url = self._get_url(pk = options['id'])

		# Debug
		if self.debug:
			print("\n== Begin '%s' %s view test\n url : %s" % (self.resource_name, action, url))

		# Test permissions for all users
		for user in self.users:
			# Re-save the object in the db in order to have the same after each user modifications
			self.object.save()

			if action in ('create', 'update'):
				options['data'] = self._get_object_attributes(self.users.get(user))
				if self.debug:
					print(" options : ", options['data'])

			# Perform the test
			self._test_user_permission(url, user, self._is_allowed(action, user), **options)

			# Additionnal test with PUT for update
			if action == 'update':
				options['method'] = 'put'
				self._test_user_permission(url, user, self._is_allowed(action, user), **options)


	# ========================================================
	# 		Tests
	# ========================================================

	def test_list_view(self):
		"""Test all users permissions to list"""
		self._perform_crud_test('list')

	def test_retrieve_view(self):
		"""Test all users permissions to retrieve self.object"""
		self._perform_crud_test('retrieve')

	def test_create_view(self):
		"""Test all users permissions to create an object"""
		self._perform_crud_test('create')

	def test_update_view(self):
		"""Test all users permissions to modify an object"""
		self._perform_crud_test('update')

	def test_delete_view(self):
		"""Test all users permissions to delete an object"""
		self._perform_crud_test('delete')

