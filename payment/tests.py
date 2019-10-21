from django.urls import reverse, exceptions
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from functools import reduce
from .helpers import OrderValidator
from authentication.models import *
from sales.models import *

from core.tests import FakeModelFactory, format_date


class OrderValidatorTestCase(APITestCase):
	
	modelFactory = FakeModelFactory()

	def setUp(self):
		now    = timezone.now()
		delay1 = timezone.timedelta(days=1)
		delay2 = timezone.timedelta(weeks=1)
		self.datetimes = {
			'before2': now - delay2,
			'before':  now - delay1,
			'now':     now,
			'after':   now + delay1,
			'after2':  now + delay2,
		}

		# Default models
		self.sale = self.modelFactory.create(Sale,
			is_active = True,
			begin_at  = self.datetimes['before'],
			end_at    = self.datetimes['after'],
			max_item_quantity = 400,
			max_payment_date  = self.datetimes['after'],
		)

		self.users = [
			self.modelFactory.create(User),	# normal
			self.modelFactory.create(User),	# other
			self.modelFactory.create(User),	# different usertype
		]
		self.user = self.users[0]

		def only_for_users(users):
			users_id = [ user.id for user in users ]
			return lambda user: user.id in users_id

		self.usertypes = [
			self.modelFactory.create(UserType, validation=only_for_users(self.users[:2])),
			self.modelFactory.create(UserType, validation=only_for_users(self.users[2:])),
		]
		self.usertype = self.usertypes[0]


		self.itemgroup = self.modelFactory.create(ItemGroup, quantity=400, max_per_user=5)
		self.items = [
			self.modelFactory.create(Item,
				sale         = self.sale,
				group        = self.itemgroup,
				usertype     = self.usertypes[0],
				is_active    = True,
				quantity     = 300,
				max_per_user = 7,
			),
			self.modelFactory.create(Item,
				sale         = self.sale,
				group        = self.itemgroup,
				usertype     = self.usertypes[1],
				is_active    = True,
				quantity     = 300,
				max_per_user = 7,
			),
		]
		self.item = self.items[0]

		self.order, self.orderline = self._create_order(self.user, self.item)

		# Test if everything is fine
		self._test_validation(True)

	def _create_order(self, user: User, item: Item=None, status: int=OrderStatus.ONGOING.value):
		"""
		Helper to create an order and one orderline
		"""
		item = item or self.items[0]
		order = self.modelFactory.create(Order,
			owner=user,
			sale=self.sale,
			created_at=self.datetimes['now'],
			updated_at=self.datetimes['now'],
			status=status,
		)
		orderline = self.modelFactory.create(OrderLine, item=item, order=order, quantity=2)
		return order, orderline


	def _test_validation(self, should_pass, order=None, messages=None, *args, **kwargs):
		"""
		Helper to test whether or not an order should pass
		"""
		if order is None:
			order = self.order

		# TODO Try to lower that
		# with self.assertNumQueries(6):
		validator = OrderValidator(order, raise_on_error=False)
		validator.validate()

		debug_msg = "Les erreurs obtenues sont : \n - " + "\n - ".join(validator.errors) if validator.errors else None
		self.assertEqual(validator.is_valid, should_pass, debug_msg)
		if messages is not None:
			self.assertEqual(message_list, messages, debug_msg)


	# =================================================
	# 		Tests
	# =================================================

	def test_sale_active(self):
		"""Inactive sales can't proceed orders"""
		self.sale.is_active = False
		self.sale.save()
		self._test_validation(False)

	def test_sale_is_ongoing(self):
		"""Orders should be paid between sales beginning date and max payment date"""
		# Cannot pay before sale
		self.sale.begin_at = self.datetimes['after']
		self.sale.max_payment_date = self.datetimes['after']
		self.sale.save()
		self._test_validation(False)

		# Cannot pay after sale
		self.sale.begin_at = self.datetimes['before']
		self.sale.max_payment_date = self.datetimes['before']
		self.sale.save()
		self._test_validation(False)

	def test_not_buyable_order(self):
		"""Orders that don't have the right status can't be bought"""
		self.order.status = OrderStatus.ONGOING.value
		self._test_validation(True)
		self.order.status = OrderStatus.AWAITING_VALIDATION.value
		self._test_validation(True)
		self.order.status = OrderStatus.AWAITING_PAYMENT.value
		self._test_validation(True)
		
		self.order.status = OrderStatus.VALIDATED.value
		self._test_validation(False)
		self.order.status = OrderStatus.PAID.value
		self._test_validation(False)
		self.order.status = OrderStatus.EXPIRED.value
		self._test_validation(False)
		self.order.status = OrderStatus.CANCELLED.value
		self._test_validation(False)

	def test_sale_max_quantities(self):
		"""Sales max quantities must be respected"""
		# Over Sale max_item_quantity
		self.sale.max_item_quantity = self.orderline.quantity - 1
		self.sale.save()
		# self._test_validation(False)

		# Limit Sale max_item_quantity
		self.sale.max_item_quantity = self.orderline.quantity
		self.sale.save()
		# self._test_validation(True)

		# Other users booked orders
		order1, orderline1 = self._create_order(self.users[1], status=OrderStatus.AWAITING_PAYMENT.value)
		order2, orderline2 = self._create_order(self.users[2], status=OrderStatus.AWAITING_PAYMENT.value)
		booked_orders = (order1, order2)

		orderlines = (self.orderline, orderline1, orderline2)
		upperLimit = reduce(lambda sum, orderline: sum + orderline.quantity, orderlines, 0)

		# Over Sale max_item_quantity
		self.sale.max_item_quantity = upperLimit - 1
		self.sale.save()
		for order in booked_orders:
			self._test_validation(True, order)
		self._test_validation(False, self.order)

		# Limit Sale max_item_quantity
		self.sale.max_item_quantity = upperLimit
		self.sale.save()
		for order in booked_orders:
			self._test_validation(True, order)
		self._test_validation(True, self.order)


	def test_item_quantities(self):
		"""Items quantities must be respected"""
		upperLimit = self.orderline.quantity

		# Over Item max_per_user
		self.item.max_per_user = upperLimit - 1
		self.item.save()
		self._test_validation(False)
		# Limit Item max_per_user
		self.item.max_per_user = upperLimit
		self.item.save()
		self._test_validation(True)

		# Over Item quantity
		self.item.quantity = upperLimit - 1
		self.item.save()
		self._test_validation(False)
		# Limit Item quantity
		self.item.quantity = upperLimit
		self.item.save()
		self._test_validation(True)

		# TODO : with other users

	def test_itemgroup_quantities(self):
		"""ItemGroups quantities must be respected"""
		upperLimit = self.orderline.quantity
 
		# Over Itemgroup quantity
		self.itemgroup.quantity = upperLimit - 1
		self.itemgroup.save()
		self._test_validation(False)
		# Limit Itemgroup quantity
		self.itemgroup.quantity = upperLimit
		self.itemgroup.save()
		self._test_validation(True)

		# Over Itemgroup max_per_user
		self.itemgroup.max_per_user = upperLimit - 1
		self.itemgroup.save()
		self._test_validation(False)
		# Limit Itemgroup max_per_user
		self.itemgroup.max_per_user = upperLimit
		self.itemgroup.save()
		self._test_validation(True)

		# TODO : with other users



