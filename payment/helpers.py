from sales.models import Order, OrderStatus
from django.utils import timezone
from functools import reduce

class OrderValidator:

	def __init__(self, order):
		# TODO : Optimize
		self.order = Order.objects.select_related('sale', 'owner') \
							.prefetch_related('orderlines', 'orderlines__item', 'sale__items', 'owner__orders') \
							.get(pk=order.pk)
		self.user = self.order.owner
		self.sale = self.order.sale
		self.errors = []

		self._bindQuantitiesToOrder()

	def _bindQuantitiesToOrder(self):
		"""
		Add a get_quantity helper in order to get item quantity easier and compute these only once
		"""
		order_quantity = reduce(lambda acc, orderline: acc + orderline.quantity, self.order.orderlines.all(), 0)
		order_quantity_per_item = { orderline.item: orderline.quantity for orderline in self.order.orderlines.all() }

		# Helper to get item quantity bought in order
		def get_quantity(item=None):
			print(order_quantity)
			return order_quantity if item else order_quantity_per_item.get(item, 0)

		self.order.get_quantity = get_quantity



	def isValid(self, *args, **kwargs):
		"""
		Vérifie la validité d'un order
		"""

		self._checkSale()
		if len(self.errors) > 0: return (False, self.errors)

		self._checkOrder()
		if len(self.errors) > 0: return (False, self.errors)

		self._checkUserPreviousOrders()
		if len(self.errors) > 0: return (False, self.errors)

		# Everything is fine
		return (True, None)



	# ===============================================
	# 			Check functions
	# ===============================================

	def _checkSale(self):
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

		# Fetch items with limited quantities
		sale_limited_items = self.sale.items.filter(quantity__gt=0)

		if self.sale.max_item_quantity > 0 or sale_limited_items:

			# 1. Retrieve all orders which book items except the one we are processing
			sale_orders = self.sale.orders \
								.filter(status__in=OrderStatus.BOOKED_LIST.value) \
								.exclude(pk=self.order.pk)

			# 2. Process quantities
			bought_quantities = { item: 0 for item in sale_limited_items }
			total_bought = 0
			for orderline in sale_orders.orderlines:
				# Add quantity to total
				total_bought += orderline.quantity

				# Add quantity to the limited item bought
				if orderline.item in bought_quantities:
					bought_quantities[orderlineitem] += orderline.quantity


			# 3. Check max item quantity for the sale (ie. enough items left)
			order_quantity = reduce(lambda acc, orderline: acc + orderline.quantity, self.order.orderlines, 0)
			if self.sale.max_item_quantity > 0 and total_bought + order_quantity > self.sale.max_item_quantity:
				self.errors.append("Il ne reste pas assez d'articles pour cette vente.")

			# Check max per user for the sale

			# 4. Check quantity left & max per user by item
			order_quantity_per_item = { orderline.item: orderline.quantity for orderline in self.order.orderlines }
			for item in order_quantity_per_item:
				if item.quantity > 0 and bought_quantities[item] + order_quantity_per_item[item] > item.quantity:
					self.errors.append("Il ne reste pas assez de %s." % item.name)






	def _checkGeneralOrder(self):
		"""
		Check general settings on the order
		"""

		# Check if order is still buyable
		if self.order.status not in OrderStatus.BUYABLE_STATUS_LIST.value:
			self.errors.append("Votre commande n'est pas payable.")

		# Check if expired
		# TODO

		# Check item quantities
		# for 


	def _checkUserPreviousOrders(self):
		prevQtByUser = {
			'byGroup': dict(),
			'byItem': dict(),
			'byItemTotal': 0
		}
		qtByGroup = dict()
		qtByUser = dict()
		qtByUserTotal = 0

		# Fetch orders made by the user
		self.userOrders = Order.objects \
						.filter(owner__pk=user.pk, sale__pk=order.sale.pk, status__in=OrderStatus.NOT_CANCELED_LIST) \
						.exclude(pk=order.pk) \
						.prefetch_related('orderlines', 'orderline__item', 'orderline__item__group')

		# Checkorders already bought by user
		for userOrder in userOrders:
			for orderline in userOrder.orderlines.all():

				# Check previous orders status for already in going order
				if userOrder.status in OrderStatus.BUYABLE_STATUS_LIST:
					self.errors.append("Vous avez déjà une commande en cours pour cette vente.")

				# Build quantities
				qtByGroup[orderline.item.group.pk] = orderline.quantity + qtByGroup.get(orderline.item.group.pk, 0)
				
				qtByUser[orderline.item.pk] = orderline.quantity + qtByUser.get(orderline.item.pk, 0)
				qtByUserTotal += orderline.quantity

		# Check User Orders
		qtByGroup, qtByUser, qtByUserTotal = userOrdersData
		errors += userOrdersErrors


		# Check group max per user
		for orderline in order.orderlines.filter(quantity__gt=0).all():
			qtByGroup[orderline.item.group.pk] = qtByGroup.get(orderline.item.group.pk, 0) - orderline.quantity
			if qtByGroup[orderline.item.group.pk] < 0:
				errors.append("Vous ne pouvez pas prendre plus de {} {} par personne." \
					.format(orderline.item.group.max_per_user, orderline.item.group.name))


