from django.urls import reverse, exceptions
from django.utils import timezone
from rest_framework import status
from django.db import transaction
from rest_framework.test import APITestCase, APITransactionTestCase, APIClient
from django import db
from time import sleep

from typing import Sequence
from collections import namedtuple
from threading import Thread
from math import ceil
import random

from core.faker import FakeModelFactory
from .helpers import OrderValidator
from authentication.models import *
from sales.models import *

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

		# TODO Try to lower the queries required to lower
		# with self.assertNumQueries(6):
		validator = OrderValidator(order, raise_on_error=False)
		validator.validate()

		debug_msg = "Les erreurs obtenues sont : \n - " + "\n - ".join(validator.errors) if validator.errors else None
		self.assertEqual(validator.is_valid, should_pass, debug_msg)
		if messages is not None:
			self.assertEqual(validator.errors, messages, debug_msg)


	# =================================================
	# 		Tests
	# =================================================

	def test_sale_active(self):
		"""
		Inactive sales can't proceed orders
		"""
		self.sale.is_active = False
		self.sale.save()
		self._test_validation(False)

	def test_sale_is_ongoing(self):
		"""
		Orders should be paid between sales beginning date and max payment date
		"""
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
		"""
		Orders that don't have the right status can't be bought
		"""
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
		"""
		Sales max quantities must be respected
		"""
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
		upperLimit = self.orderline.quantity + orderline1.quantity + orderline2.quantity

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
		"""
		Items quantities must be respected
		"""
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
		"""
		ItemGroups quantities must be respected
		"""
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

class ShotgunTestCase(APITransactionTestCase):

	modelFactory = FakeModelFactory()

	n_users = 10
	n_items = 2
	max_quantity = n_users - 1

	def setUp(self):
		"""
		Set up the shotgun
		"""
		if self.n_users <= self.n_items:
			raise ValueError("There must be more items than users") 
		if self.n_users <= self.max_quantity:
			raise ValueError("Max quantity must be less than the number of users") 

		with transaction.atomic():
			# Create sale
			self.sale = self.modelFactory.create(Sale, max_item_quantity=None)
			self.usertype = self.modelFactory.create(UserType, validation=lambda user: True)
			self.group = self.modelFactory.create(ItemGroup, quantity=None, max_per_user=None)
			self.items = [
				self.modelFactory.create(Item,
					sale=self.sale, usertype=self.usertype, group=self.group,
					quantity=None, max_per_user=None
				) for _ in range(self.n_items)
			]

			# Create users and clients
			self.users = []
			self.clients = []
			for _ in range(self.n_users):
				user = self.modelFactory.create(User)
				client = APIClient(enforce_csrf_checks=True)
				client.force_authenticate(user=user)
				self.users.append(user)

				self.clients.append(client)
		db.connections.close_all()

	@classmethod
	def tearDownClass(cls):
		super().tearDownClass()
		db.connections.close_all()
		# TODO FIXME There are 6 other sessions using the database.
		import ipdb; ipdb.set_trace()

	def _debug_response(self, resp) -> str:
		try:
			return f" ({resp.json()['error']})"
		except:
			return ""

	def _shotgun(self, client: APIClient, item: Item, quantity: int=1):
		"""
		Shotgun an item from a client
		
		Arguments:
			client (APIClient): the client to shotgun with
			item (Item):        the item to shotgun
			quantity (int):     the quantity to shotgun (default: {1})
		"""
		# Create order
		order_resp = client.post(f"/sales/{self.sale.id}/orders", {})
		self.assertEqual(order_resp.status_code, 201,
		                 "Order response is not valid" + self._debug_response(order_resp))

		order = order_resp.json()
		order_id = order['id']
		self.assertTrue(order_id, "Didn't receive an order id")
		self.assertFalse(order['orderlines'], "Orderlines should be empty")
		self.assertEqual(order['status'], OrderStatus.ONGOING.value,
		                 f"Order should be ONGOING ({OrderStatus(order['status']).name})")

		# Create orderlines
		orderline_resp = client.post(f"/orders/{order_id}/orderlines", {
			'item': item.id,
			'quantity': quantity,
		})
		self.assertEqual(orderline_resp.status_code, 201,
		                 "Orderline response is not valid" + self._debug_response(order_resp))

		# Pay order and add pay response
		pay_resp = client.get(f"/orders/{order_id}/pay?return_url=http://localhost:3000/orders/{order_id}")
		self.responses.append(pay_resp)

	def _test_shotgun(self, items: Sequence[Item]=None, quantity_per_request: int=1):
		self.responses = []
		if items is None:
			items = self.items

		# Create jobs
		jobs = []
		n_requests = self.n_users # ceil(self.max_quantity / quantity_per_request)
		for i in range(n_requests):
			client = self.clients[i % self.n_users]
			item = random.choice(items)
			jobs.append(Thread(target=self._shotgun, args=(client, item, quantity_per_request)))

		# Start jobs and wait for them to finish
		for job in jobs:
			job.start()
		for job in jobs:
			job.join()
			del job

		# Analyse responses
		nb_success = nb_awaiting = 0
		for resp in self.responses:
			nb_success += resp.status_code == 200
			nb_awaiting += resp.data.get('status') == OrderStatus.AWAITING_PAYMENT.name
		self.assertEqual(nb_success, self.max_quantity)
		self.assertEqual(nb_awaiting, self.max_quantity)
		# TODO Test more

	def test_sale_quantity(self):
		self.sale.max_item_quantity = self.max_quantity
		self.sale.save()
		self._test_shotgun()

	def test_group_quantity(self):
		self.group.quantity = self.max_quantity
		self.group.save()
		self._test_shotgun()

	def test_item_quantity(self):
		for item in self.items:
			item.quantity = self.max_quantity
			item.save()
			self._test_shotgun(items=[item])




