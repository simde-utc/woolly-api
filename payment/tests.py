from django.urls import reverse, exceptions
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .helpers import OrderValidator
from authentication.models import *
from sales.models import *

from core.tests import FakeModelFactory, format_date
from faker import Faker

faker = Faker()
modelFactory = FakeModelFactory()

class OrderValidatorTestCase(APITestCase):

	def setUp(self):
		self.datetimes = {
			'before': 	format_date(faker.date_time_this_year(before_now=True, 	after_now=False)),
			'after':  	format_date(faker.date_time_this_year(before_now=False, after_now=True)),
			'now': 		timezone.now(),
		}
		# Default models
		self.usertype = modelFactory.create(UserType)
		self.user = modelFactory.create(User, usertype=self.usertype)

		self.sale = modelFactory.create(Sale,
			is_active 	= True,
			begin_at 	= self.datetimes['before'],
			end_at 		= self.datetimes['after'],
			max_item_quantity = 400,
			max_payment_date = self.datetimes['after']
		)
		self.itemgroup = modelFactory.create(ItemGroup, quantity=400, max_per_user=5)
		self.item = modelFactory.create(Item,
			sale = 	self.sale,
			group = self.itemgroup,
			usertype = self.usertype,
			is_active = True,
			quantity = 300,
			max_per_user = 7,
		)
		
		self.order = modelFactory.create(Order,
			owner = self.user,
			sale = self.sale,
			created_at = self.datetimes['now'],
			updated_at = self.datetimes['now'],
			status = OrderStatus.ONGOING.value,
		)

		self.orderline = modelFactory.create(OrderLine, item=self.item, order=self.order, quantity=2)
		self._test_validation(True)


	def _test_validation(self, should_fail, messages=None, *args, **kwargs):
		# TODO Try to lower that
		with self.assertNumQueries(6):
			validator = OrderValidator(self.order)
			has_errors, message_list = validator.isValid(processAll=kwargs.get('processAll', True))

		debug_msg = None if message_list is None else "Les erreurs obtenues sont : " + "\n - ".join(message_list)
		self.assertEqual(has_errors, should_fail, debug_msg)
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
		self.sale.begin_at = self.datetimes['after']
		self.sale.max_payment_date = self.datetimes['after']
		self.sale.save()
		self._test_validation(False)

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
		self.order.status = OrderStatus.NOT_PAID.value
		self._test_validation(True)
		
		self.order.status = OrderStatus.VALIDATED.value
		self._test_validation(False)
		self.order.status = OrderStatus.PAID.value
		self._test_validation(False)
		self.order.status = OrderStatus.EXPIRED.value
		self._test_validation(False)
		self.order.status = OrderStatus.CANCELLED.value
		self._test_validation(False)

