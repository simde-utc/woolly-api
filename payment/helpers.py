from sales.models import Order, OrderLine, OrderStatus
from django.utils import timezone
from functools import reduce
from typing import List

class OrderValidationException(Exception):
	pass

class OrderValidator:
	"""
	Object that can validate an order
	"""

	def __init__(self, order: Order, raise_on_error: bool=True):
		# TODO : Optimize
		# self.order = Order.objects.select_related('sale', 'owner') \
		# 					.prefetch_related('orderlines', 'orderlines__item', 'sale__items', 'owner__orders') \
		# 					.get(pk=order.pk)
		self.order = order
		self.user = self.order.owner
		self.sale = self.order.sale

		self.raise_on_error = raise_on_error
		self.now = timezone.now()
		self.errors = []
		self.checked = False

	def validate(self):
		"""
		Vérifie la validité d'un order
		"""
		self.checked = True
		self._check_sale()
		self._check_order()
		self._check_quantities()

	@property
	def is_valid(self) -> bool:
		if not self.checked:
			raise OrderValidationException("Must launch the validation process before")
		return len(self.errors) == 0

	def get_errors(self) -> List[str]:
		return self.errors

	def _add_error(self, error: str):
		"""Raise or add a new error"""
		self.errors.append(error)
		if self.raise_on_error:
			raise Exception(error)


	# ===============================================
	# 			Check functions
	# ===============================================

	def _check_sale(self):
		"""
		Check general settings on the sale
		"""
		# Check if sale is active
		if not self.sale.is_active:
			self._add_error("La vente n'est pas disponible.")

		# Check dates
		if self.now < self.sale.begin_at:
			self._add_error("La vente n'a pas encore commencé.")
		if self.now > self.sale.end_at:
			self._add_error("La vente est terminée.")
		if self.now > self.sale.max_payment_date:
			self._add_error("Le paiement n'est plus possible.")

	def _check_order(self):
		"""
		Check general settings on the order
		"""
		# Check if order is still buyable
		if self.order.status not in OrderStatus.BUYABLE_STATUS_LIST.value:
			self._add_error("Votre commande n'est pas payable.")

		# Check if expired
		# TODO

		# Check if no previous ongoing order
		user_prev_ongoing_orders = self.user.orders.filter(status=OrderStatus.ONGOING.value).exclude(pk=self.order.pk)
		if len(user_prev_ongoing_orders) > 0:
			self._add_error("Vous avez déjà une commande en cours pour cette vente.")

	def _check_quantities(self):
		"""
		Fetch, Process and Verify Quantities
		"""
		# ======= Part I - Fetch resources
		# TODO : optimize (orderlinefield.orderlineitem.orderline.order.sale.association)

		# sale_items = self.sale.items.prefetch_related('group').all()
		order_orderlines = self.order.orderlines.prefetch_related('item').all()
		# All orders which book items except the one we are processing
		sale_orderlines = OrderLine.objects \
							.filter(order__sale__pk=self.sale.pk, order__status__in=OrderStatus.BOOKED_LIST.value) \
							.exclude(order__pk=self.order.pk) \
							.prefetch_related('item', 'item__group')
		# Orders that the user already booked
		user_orderlines = sale_orderlines.filter(order__owner__pk=self.user.pk)


		# ======= Part II - Process quantities

		def build_quantity(orderlines) -> list:
			def _reducer(acc: list, orderline: OrderLine) -> list:
				acc[0] += orderline.quantity
				acc[1][orderline.item] = acc[1].get(orderline.item, 0) + orderline.quantity
				if orderline.item.group:
					acc[2][orderline.item.group] = acc[2].get(orderline.item.group, 0) + orderline.quantity
				return acc
			return reduce(_reducer, orderlines, [0, {}, {}])

		# Quantity per item and Total quantity bought in the order
		order_total_qt, order_qt_per_item, order_qt_per_group = build_quantity(order_orderlines)
		sale_total_qt,  sale_qt_per_item,  sale_qt_per_group  = build_quantity(sale_orderlines)
		user_total_qt,  user_qt_per_item,  user_qt_per_group  = build_quantity(user_orderlines)


		# ======= Part III - Verification

		def is_quantity(quantity) -> bool:
			return type(quantity) is int and quantity > 0

		# III.1 - Sale level verification

		# TODO
		if order_total_qt <= 0:
			self._add_error("Vous devez avoir un nombre d'items commandés strictement positif.")

		# Check max item quantity for the sale (ie. enough items left)
		if is_quantity(self.sale.max_item_quantity) and sale_total_qt + order_total_qt > self.sale.max_item_quantity:
			self._add_error("Il ne reste pas assez d'articles pour cette vente.")

		# Check max per user for the sale
		# TODO

		# III.2 - Item level verification
		for item in order_qt_per_item:
			# Check quantity per item
			if is_quantity(item.quantity) and sale_qt_per_item.get(item, 0) + order_qt_per_item[item] > item.quantity:
				self._add_error("Il ne reste pas assez de %s." % item.name)

			# Check max_per_user per item 
			if is_quantity(item.quantity) and user_qt_per_item.get(item, 0) + order_qt_per_item[item] > item.max_per_user:
				self._add_error("Vous ne pouvez pas prendre plus de %d %s par utilisateur." % (item.max_per_user, item.name))

		# III.3 - ItemGroup level verification
		for group in order_qt_per_group:
			# Check quantity per group
			if is_quantity(group.quantity) and sale_qt_per_group.get(group, 0) + order_qt_per_group[group] > group.quantity:
				self._add_error("Il ne reste pas assez de %s." % group.name)

			# Check max_per_user per group
			if is_quantity(group.quantity) and user_qt_per_group.get(group, 0) + order_qt_per_group[group] > group.max_per_user:
				self._add_error("Vous ne pouvez pas prendre plus de %d %s par utilisateur." % (group.max_per_user, group.name))

