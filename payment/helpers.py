from sales.models import Order, OrderLine, OrderStatus
from django.utils import timezone
from functools import reduce

class OrderValidator:

	def __init__(self, order, *args, **kwargs):
		# TODO : Optimize
		# self.order = Order.objects.select_related('sale', 'owner') \
		# 					.prefetch_related('orderlines', 'orderlines__item', 'sale__items', 'owner__orders') \
		# 					.get(pk=order.pk)
		self.order = order
		self.user = self.order.owner
		self.sale = self.order.sale
		self.errors = []


	def isValid(self, *args, **kwargs):
		"""
		Vérifie la validité d'un order
		"""
		processAll = kwargs.get('processAll', False)

		self._checkSale()
		if not processAll and self.errors: return (False, self.errors)

		self._checkOrder()
		if not processAll and self.errors: return (False, self.errors)

		self._checkQuantities()
		if not processAll and self.errors: return (False, self.errors)

		# Final check
		return (False, self.errors) if self.errors else (True, None)


	# ===============================================
	# 			Check functions
	# ===============================================

	def _checkSale(self):
		"""Check general settings on the sale"""

		# Check if sale is active
		if not self.sale.is_active:
			self.errors.append("La vente n'est pas disponible.")

		# Check dates
		now = timezone.now()
		if now < self.sale.begin_at:
			self.errors.append("La vente n'a pas encore commencé.")
		if now > self.sale.end_at:
			self.errors.append("La vente est terminée.")
		if now > self.sale.max_payment_date:
			self.errors.append("Le paiement n'est plus possible.")


	def _checkOrder(self):
		"""Check general settings on the order"""

		# Check if order is still buyable
		if self.order.status not in OrderStatus.BUYABLE_STATUS_LIST.value:
			self.errors.append("Votre commande n'est pas payable.")

		# Check if expired
		# TODO

		# Check if no previous ongoing order
		user_previous_ongoing_orders = self.user.orders.filter(status=OrderStatus.ONGOING.value).exclude(pk=self.order.pk)
		if len(user_previous_ongoing_orders) > 0:
			self.errors.append("Vous avez déjà une commande en cours pour cette vente.")


	def _checkQuantities(self):
		"""Fetch, Process and Verify Quantities"""

		###############################################
		# 		Part I - Fetch resources
		###############################################
		# TODO : optimize (orderlinefield.orderlineitem.orderline.order.sale.association)

		sale_items = self.sale.items.all()
		order_orderlines = self.order.orderlines.prefetch_related('item').all()
		# All orders which book items except the one we are processing
		sale_orderlines = OrderLine.objects \
							.filter(order__sale__pk=self.sale.pk, order__status__in=OrderStatus.BOOKED_LIST.value) \
							.exclude(order__pk=self.order.pk) \
							.prefetch_related('item', 'item__group')
		user_orderlines = sale_orderlines.filter(order__owner__pk=self.user.pk)


		###############################################
		# 		Part II - Process quantities
		###############################################

		def quantityBuilder(orderlines):
			def reducerFunc(acc, orderline):
				acc[0] += orderline.quantity
				acc[1][orderline.item] = acc[1].get(orderline.item, 0) + orderline.quantity
				if orderline.item.group:
					acc[2][orderline.item.group] = acc[2].get(orderline.item.group, 0) + orderline.quantity
				return acc
			return reduce(reducerFunc, orderlines, [0, {}, {}])

		# Quantity per item and Total quantity bought in the order
		order_total_qt, order_qt_per_item, order_qt_per_group = quantityBuilder(order_orderlines)
		sale_total_qt,  sale_qt_per_item,  sale_qt_per_group  = quantityBuilder(sale_orderlines)
		user_total_qt,  user_qt_per_item,  user_qt_per_group  = quantityBuilder(user_orderlines)


		###############################################
		# 		Part III - Verification
		###############################################

		def isQuantity(quantity):
			return type(quantity) is int and quantity > 0

		# III.1 - Sale level verification

		# Check max item quantity for the sale (ie. enough items left)
		if isQuantity(self.sale.max_item_quantity) and sale_total_qt + order_total_qt > self.sale.max_item_quantity:
			self.errors.append("Il ne reste pas assez d'articles pour cette vente.")

		# Check max per user for the sale
		# TODO

		# III.2 - Item level verification
		for item in order_qt_per_item:
			# Check quantity per item
			if isQuantity(item.quantity) and sale_qt_per_item.get(item, 0) + order_qt_per_item[item] > item.quantity:
				self.errors.append("Il ne reste pas assez de %s." % item.name)

			# Check max_per_user per item 
			if isQuantity(item.quantity) and user_qt_per_item.get(item, 0) + order_qt_per_item[item] > item.max_per_user:
				self.errors.append("Vous ne pouvez pas prendre plus de %d %s par utilisateur." % (item.max_per_user, item.name))

		# III.3 - ItemGroup level verification
		for group in order_qt_per_group:
			# Check quantity per group
			if isQuantity(group.quantity) and sale_qt_per_group.get(group, 0) + order_qt_per_group[group] > group.quantity:
				self.errors.append("Il ne reste pas assez de %s." % group.name)

			# Check max_per_user per group
			if isQuantity(group.quantity) and user_qt_per_group.get(group, 0) + order_qt_per_group[group] > group.max_per_user:
				self.errors.append("Vous ne pouvez pas prendre plus de %d %s par utilisateur." % (group.max_per_user, group.name))



