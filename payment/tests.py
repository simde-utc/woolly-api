from typing import Sequence
from collections import Counter
from threading import Thread
import random

from django.utils import timezone
from django.db import transaction
from django.test import tag
from rest_framework.test import APITestCase, APITransactionTestCase


from core.faker import FakeModelFactory
from core.testcases import get_api_client
from authentication.models import User, UserType
from sales.models import Sale, Item, ItemGroup, Order, OrderStatus, OrderLine, OrderLineItem
from payment.validator import OrderValidator


def start_and_await_jobs(jobs: Sequence[Thread]) -> None:
    """
    Start jobs and wait for them to finish

    Arguments:
        jobs (Sequence[Thread]): the jobs to run and close
    """
    jobs = tuple(jobs)
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()


@tag('validation')
class OrderValidatorTestCase(APITestCase):

    factory = FakeModelFactory()

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
        self.sale = self.factory.create(
            Sale,
            is_active = True,
            begin_at  = self.datetimes['before'],
            end_at    = self.datetimes['after'],
            max_item_quantity = 400,
        )

        self.users = [
            self.factory.create(User),  # normal
            self.factory.create(User),  # other
            self.factory.create(User),  # different usertype
        ]
        self.user = self.users[0]

        def only_for_users(users) -> str:
            users_id = [ str(user.id) for user in users ]
            return f"str(user.id) in {users_id}"

        self.usertypes = [
            self.factory.create(UserType, validation=only_for_users(self.users[:2])),
            self.factory.create(UserType, validation=only_for_users(self.users[2:])),
        ]
        self.usertype = self.usertypes[0]

        # Create items
        rand = self.factory.faker.random_int
        self.itemgroup = self.factory.create(
            ItemGroup,
            quantity=rand(min=200, max=400),
            max_per_user=rand(min=5, max=10),
        )
        self.items = [
            self.factory.create(
                Item,
                sale         = self.sale,
                group        = self.itemgroup,
                usertype     = self.usertypes[0],
                is_active    = True,
                quantity     = rand(min=200, max=400),
                max_per_user = rand(min=2, max=5),
            ),
            self.factory.create(
                Item,
                sale         = self.sale,
                group        = self.itemgroup,
                usertype     = self.usertypes[1],
                is_active    = True,
                quantity     = rand(min=200, max=400),
                max_per_user = rand(min=2, max=5),
            ),
        ]
        self.item = self.items[0]

        items = [ *self.items, self.itemgroup ]
        self.min_max_per_user = min([ item.max_per_user for item in items ])
        self.min_quantity = min([ item.quantity for item in items ])

        self.order, self.orderline = self._create_order(self.user, self.item)

        # Test if everything is fine
        self._test_validation(True)

    def _create_order(self, user: User, item: Item=None, status: int=OrderStatus.ONGOING.value):
        """
        Helper to create an order and one orderline
        """
        item = item or self.items[0]
        order = self.factory.create(
            Order,
            owner=user,
            sale=self.sale,
            created_at=self.datetimes['now'],
            updated_at=self.datetimes['now'],
            status=status,
        )
        qt = self.factory.faker.random_int(min=2, max=min(self.min_max_per_user, self.min_quantity))
        orderline = self.factory.create(OrderLine, item=item, order=order, quantity=qt)
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
    #       Tests
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
        self.sale.end_at = self.datetimes['after']
        self.sale.save()
        self._test_validation(False)

        # Cannot pay after sale
        self.sale.begin_at = self.datetimes['before']
        self.sale.end_at = self.datetimes['before']
        self.sale.save()
        self._test_validation(False)

    def test_usertype_verification(self):
        """
        Item for special usertype should only be buyable
        by users that validate the usertype
        """
        self.order.delete()
        for item in self.items:
            for user in self.users:
                should_pass = item.usertype.check_user(user)
                order, __ = self._create_order(user, item)
                self._test_validation(should_pass, order)
                order.delete()

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

    @tag('quantities')
    def test_sale_max_quantities(self):
        """
        Sales max quantities must be respected
        """
        upperLimit = self.orderline.quantity

        # Over Sale max_item_quantity
        self.sale.max_item_quantity = upperLimit - 1
        self.sale.save()
        self._test_validation(False)
        # Limit Sale max_item_quantity
        self.sale.max_item_quantity = upperLimit
        self.sale.save()
        self._test_validation(True)

        # Other users booked orders
        order1, orderline1 = self._create_order(self.users[1], self.items[0],
                                                status=OrderStatus.AWAITING_PAYMENT.value)
        order2, orderline2 = self._create_order(self.users[2], self.items[1],
                                                status=OrderStatus.AWAITING_PAYMENT.value)
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

    @tag('quantities')
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

    @tag('quantities')
    def test_item_max_per_user(self):
        """
        Items max_per_user must be respected
        """
        upperLimit = self.orderline.quantity

        # Over Item quantity
        self.item.quantity = upperLimit - 1
        self.item.save()
        self._test_validation(False)
        # Limit Item quantity
        self.item.quantity = upperLimit
        self.item.save()
        self._test_validation(True)

    @tag('quantities')
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

    @tag('quantities')
    def test_itemgroup_max_per_user(self):
        """
        ItemGroups max_per_user must be respected
        """
        upperLimit = self.orderline.quantity

        # Over Itemgroup max_per_user
        self.itemgroup.max_per_user = upperLimit - 1
        self.itemgroup.save()
        self._test_validation(False)
        # Limit Itemgroup max_per_user
        self.itemgroup.max_per_user = upperLimit
        self.itemgroup.save()
        self._test_validation(True)


@tag('validation', 'shotgun')
class ShotgunTestCase(APITransactionTestCase):

    factory = FakeModelFactory()

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

        # Create sale and users
        with transaction.atomic():
            self.sale = self.factory.create(Sale, max_item_quantity=None)
            self.usertype = self.factory.create(UserType, validation='True')
            self.group = self.factory.create(ItemGroup, quantity=None, max_per_user=None)
            self.items = [
                self.factory.create(
                    Item,
                    sale=self.sale,
                    group=self.group,
                    usertype=self.usertype,
                    quantity=None,
                    max_per_user=None
                ) for _ in range(self.n_items)
            ]
            self.users = [ self.factory.create(User) for _ in range(self.n_users) ]

    # =================================================
    #       Tests quantity in case of shotgun
    # =================================================

    def shotgun(self, user: User, item: Item, quantity: int=1):
        """
        Shotgun an item from a user

        Arguments:
            user (User):    the user to shotgun with
            item (Item):    the item to shotgun
            quantity (int): the quantity to shotgun (default: {1})
        """
        with get_api_client(user) as client:
            # Create order
            order_resp = client.post(f"/sales/{self.sale.id}/orders", {})
            msg = f"Order response is not valid ({order_resp.json()})"
            self.assertEqual(order_resp.status_code, 201, msg)

            # Check order response
            order = order_resp.json()
            order_id = order['id']
            self.assertTrue(order_id, "Didn't receive an order id")
            self.assertFalse(order['orderlines'], "Orderlines should be empty")
            msg = f"Order should be ONGOING ({OrderStatus(order['status']).name})"
            self.assertEqual(order['status'], OrderStatus.ONGOING.value, msg)

            # Create orderlines
            orderline_resp = client.post(f"/orders/{order_id}/orderlines", {
                'item': item.id,
                'quantity': quantity,
            })
            msg = f"Orderline response is not valid ({orderline_resp.json()})"
            self.assertEqual(orderline_resp.status_code, 201, msg)

            # Pay order and add pay response
            pay_resp = client.get(f"/orders/{order_id}/pay?return_url=http://localhost:3000/orders/{order_id}")
            self.responses.append(pay_resp)

    def start_shotguns(self, items: Sequence[Item]=None, max_quantity: int=None, quantity_per_request: int=1):
        """
        Shotgun items with multiple user accounts

        Arguments:
            items (Sequence[Item]):     the items to shotgun (default: self.items)
            max_quantity (int):         the max quantity of orders that should pass (default: self.max_quantity)
            quantity_per_request (int): the items quantity to shotgun per user request (default: 1)
        """
        self.responses = []
        if items is None:
            items = self.items
        if max_quantity is None:
            max_quantity = self.max_quantity

        # Create jobs to shotgun
        start_and_await_jobs((
            Thread(
                target=self.shotgun,
                args=(user, random.choice(items), quantity_per_request)
            ) for user in self.users
        ))

        # Analyse responses
        nb_success = nb_awaiting = 0
        for resp in self.responses:
            nb_success += resp.status_code == 200
            nb_awaiting += resp.json().get('status') == OrderStatus.AWAITING_PAYMENT.name
        self.assertEqual(nb_success, max_quantity)
        self.assertEqual(nb_awaiting, max_quantity)

    @tag('quantities')
    def test_sale_quantity(self):
        """
        Test that the Sale max quantity is respected even under pressure
        """
        self.sale.max_item_quantity = self.max_quantity
        self.sale.save()
        self.start_shotguns()

    @tag('quantities')
    def test_group_quantity(self):
        """
        Test that the ItemGroup max quantity is respected even under pressure
        """
        self.group.quantity = self.max_quantity
        self.group.save()
        self.start_shotguns()

    @tag('quantities')
    def test_item_quantity(self):
        """
        Test that the Item max quantity is respected even under pressure
        """
        item = self.items[0]
        item.quantity = self.max_quantity
        item.save()
        self.start_shotguns(items=[item])

    # =================================================
    #       Tests tickets generation
    # =================================================

    def pay_callback(self, user: User, order_id: str):
        """
        Request the pay callback of a specified order

        Arguments:
            user (User):    the user to login the client with
            order_id (str): the id of the order to callback
        """
        with get_api_client(user) as client:
            resp = client.get(f"/orders/{order_id}/status")
            self.responses.append(resp)

    @tag('tickets')
    def test_orderlineitems_generation(self):
        """
        Test that the OrderLineItems are generated only once and in good quantity
        """
        # Buy orders
        self.start_shotguns(max_quantity=self.n_users)
        orders = [
            resp.json()['redirect_url'].split('/', 2)[1] for resp in self.responses
        ]

        # Start jobs and wait for them to finish
        n_loops = 2
        self.responses = []
        start_and_await_jobs((
            Thread(target=self.pay_callback, args=(user, order))
            for __ in range(n_loops)
            for user, order in zip(self.users, orders)
        ))

        # Key-value counter of the response's JSON data
        kv_acc = Counter(( kv for resp in self.responses for kv in resp.json().items() ))
        n_orders = self.n_users
        n_requests = n_loops * n_orders

        # Test tickets generation happens only once
        self.assertEqual(len(self.responses), n_requests, "Didn't get as much responses as expected")
        self.assertEqual(kv_acc[('status', OrderStatus.PAID.name)], n_requests, "All orders weren't set as PAID")
        self.assertEqual(kv_acc[('updated', True)], n_orders, "Orders should be updated only once")
        self.assertEqual(kv_acc[('tickets_generated', True)], n_orders, "Tickets should be generated only once")

        # Check OrderLineItems quantity
        n_orderlineitems = OrderLineItem.objects.count()
        self.assertEqual(n_orderlineitems, n_orders, "Wrong number of tickets generated")
