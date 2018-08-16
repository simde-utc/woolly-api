from sales.models import Order, OrderStatus
from django.utils import timezone



class OrderValidator:

	def __init__(self, user, order):
		self.user = user
		self.order = order
		self.sale = order.sale
		self.errors = list()

	def isValid(self):
		"""
		Vérifie la validité d'un order

		"""

		self._checkGeneralOrder()
		if len(self.errors) > 0:		# Checkpoint
			return (False, self.errors)



		# Everything is fine
		return (True, None)


	# ===============================================
	# 			Check functions
	# ===============================================

	def _checkGeneralOrder(self):
		"""
		Check general settings on the order
		"""

		# Check if order is still buyable
		if self.order.status not in OrderStatus.BUYABLE_STATUS_LIST.value:
			self.errors.append("Votre commande n'est pas payable.")

		# Check if sale is active
		if not self.order.sale.is_active:
			self.errors.append("La vente n'est pas disponible.")

		# Check date
		now = timezone.now()
		if now < self.order.sale.begin_at:
			self.errors.append("La vente n'a pas encore commencé.")
		if now > self.order.sale.end_at:
			self.errors.append("La vente est terminée.")

	def _checkUserRightOnSale(self):
		pass

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
						.prefetch_related('orderlines').prefetch_related('orderline__item') \
						.prefetch_related('orderline__item__group')

		# Checkorders already bought by user
		for userOrder in userOrders:
			for orderline in userOrder.orderlines.all():

				# Check previous orders
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


