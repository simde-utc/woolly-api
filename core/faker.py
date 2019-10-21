from core.helpers import format_date
from faker import Faker

from authentication.models import *
from sales.models import *


class FakeModelFactory:

	def __init__(self, seed=None):
		self.faker = Faker()
		if seed:
			self.faker.seed(seed)

	def create(self, model, nb: int=None, **kwargs):
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
			return getattr(related, 'pk', None) if withPk else related

		# ============================================
		# 	Authentication
		# ============================================

		if model == User:
			return {
				'id':         kwargs.get('id',         self.faker.uuid4()),
				'email':      kwargs.get('email',      self.faker.email()),
				'first_name': kwargs.get('first_name', self.faker.first_name()),
				'last_name':  kwargs.get('last_name',  self.faker.last_name()),
				'is_admin':   kwargs.get('is_admin',   False),
				# 'types':      kwargs.get('types',      _get_related('usertype', UserType)),
			}

		if model == UserType:
			return {
				'id':   kwargs.get('id',   self.faker.uuid4()[:25]),
				'name': kwargs.get('name', self.faker.sentence(nb_words=4)),
				'validation': kwargs.get('validation', 'False'),
			}

		# ============================================
		# 	Association & Sale
		# ============================================

		if model == Association:
			return {
				'id':        kwargs.get('id',      self.faker.uuid4()),
				'shortname': kwargs.get('name',    self.faker.company()),
				'fun_id':    kwargs.get('fun_id',  self.faker.random_digit()),
			}

		# if model == AssociationMember:
	
		if model == Sale:
			return {
				'name':         kwargs.get('name',          self.faker.company()),
				'description':  kwargs.get('description',   self.faker.paragraph()),
				'association':  _get_related('association', Association),
				'is_active':    kwargs.get('is_active',     True),
				'public':       kwargs.get('public',        True),
				'begin_at':     format_date(kwargs.get('begin_at',
					self.faker.date_time_this_year(before_now=True, after_now=False)
				)),
				'end_at':       format_date(kwargs.get('end_at',
					self.faker.date_time_this_year(before_now=False, after_now=True)
				)),
				'max_item_quantity': kwargs.get('max_item_quantity', self.faker.random_number()),
				'max_payment_date':  format_date(kwargs.get('max_payment_date',
					self.faker.date_time_this_year(before_now=False, after_now=True)
				)),
			}

		# ============================================
		# 	Item & ItemGroup
		# ============================================

		if model == ItemGroup:
			return {
				'name':          kwargs.get('name',         self.faker.word()),
				'quantity':      kwargs.get('quantity',     self.faker.random_number()),
				'max_per_user':  kwargs.get('max_per_user', self.faker.random_number()),
			}

		if model == Item:
			return {
				'name':          kwargs.get('name',         self.faker.word()),
				'description':   kwargs.get('description',  self.faker.paragraph()),
				'sale':          _get_related('sale',       Sale),
				'group':         _get_related('group',      ItemGroup),
				'usertype':      _get_related('usertype',   UserType),
				'quantity':      kwargs.get('quantity',     self.faker.random_number()),
				'max_per_user':  kwargs.get('max_per_user', self.faker.random_number()),
				'is_active':     kwargs.get('is_active',    True),
				'quantity':      kwargs.get('quantity',     self.faker.random_number()),
				'price':         float(kwargs.get('price',  self.faker.random_number()/10.)),
				'nemopay_id':    kwargs.get('nemopay_id',   self.faker.random_number()),
				'max_per_user':  kwargs.get('max_per_user', self.faker.random_number()),
				# 'fields':
			}

		# ============================================
		# 	Order, OrderLine, OrderLineItem
		# ============================================

		if model == Order:
			return {
				'owner':      _get_related('owner', User),
				'sale':       _get_related('sale',  Sale),
				'created_at': format_date(kwargs.get('created_at', 
					self.faker.date_time_this_year(before_now=True, after_now=False)
				)),
				'updated_at': format_date(kwargs.get('updated_at', 
					self.faker.date_time_this_year(before_now=True, after_now=False)
				)),
				'status': kwargs.get('status', OrderStatus.ONGOING.value),
				'tra_id': kwargs.get('tra_id', self.faker.random_number()),
			}

		if model == OrderLine:
			return {
				'item':     _get_related('item',   Item),
				'order':    _get_related('order',  Order),
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
				'name':     kwargs.get('name',    self.faker.word()),
				'type':     kwargs.get('type',    self.faker.word()),
				'default':  kwargs.get('default', self.faker.word()),
				# 'items': 	
			}

		if model == ItemField:
			return {
				'field':    _get_related('field',  Field),
				'item':     _get_related('item',   Item),
				'editable': kwargs.get('editable', self.faker.boolean()),
			}

		if model == OrderLineField:
			return {
				'orderlineitem': _get_related('orderlineitem', OrderLineItem),
				'field':         _get_related('field', Field),
				'value':         kwargs.get('value',   self.faker.word()),
			}

		raise NotImplementedError("This model isn't faked yet")

