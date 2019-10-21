from sales.models import *
import pandas as pd
from payment.services.payutc import Payutc
from woolly_api.settings import EXPORTS_DIR, PAYUTC_KEY, MAX_ONGOING_TIME, MAX_PAYMENT_TIME
from payment.views import updateOrderStatus, createOrderLineItemsAndFields
from os import path
from tqdm.auto import tqdm
from django.utils import timezone
from django.db.models import Count


def full_process(sale_pk: int=None, backup_after: bool=False):
	dump_sale_excel(sale_pk)
	update_orders(sale_pk)
	verify_orderlines(sale_pk)
	gen_tickets(sale_pk)
	if backup_after:
		dump_sale_excel(sale_pk)

def _export_name(prefix: str, sale_pk: int=None):
	dt = str(timezone.now())[:19].replace(':', '-')
	_id = ('all' if sale_pk is None else sale_pk)
	return path.join(EXPORTS_DIR, "{}_{}_{}.xlsx".format(prefix, _id, dt))

def dump_cat_excel(sale_pk: int=None):
	orders = Order.objects.prefetch_related('owner', 'orderlines', 'orderlines__orderlineitems',
																					'orderlines__orderlineitems__orderlinefields',
																					'orderlines__orderlineitems__orderlinefields__field') \
												.filter(status=OrderStatus.PAID.value)
	if sale_pk is not None:
		orders = orders.filter(sale_id=sale_pk)

	def _proccess_order(order):
		data_list = []
		for orderline in order.orderlines.all():
			for orderlineitem in orderline.orderlineitems.all():
				data = { orderlinefield.field.name: orderlinefield.value
									for orderlinefield in orderlineitem.orderlinefields.all() }
				data.update({
					'UUID': orderlineitem.id.replace('-', ''), # Remove dashes for wap
					'Email Acheteur': order.owner.email,
					'Item':	orderline.item.name,
				})
				data_list.append(data)
		return data_list

	results = pd.DataFrame([ data for order in tqdm(orders.all(), desc='Processing orders...')
															 for data in _proccess_order(order) ])
	results.to_excel(_export_name("dump_cat", sale_pk))
	print("Dumped sale.")


def dump_sale_excel(sale_pk: int=None):
	"""
	Dump all the orders of a sale into an excel file
	"""
	orders = Order.objects.prefetch_related('owner', 'orderlines', 'orderlines__orderlineitems',
																					'orderlines__orderlineitems__orderlinefields',
																					'orderlines__orderlineitems__orderlinefields__field') \
												.filter(status=OrderStatus.PAID.value)
	if sale_pk is not None:
		orders = orders.filter(sale_id=sale_pk)

	def _proccess_order(order):
		data_list = []
		for orderline in order.orderlines.all():
			for orderlineitem in orderline.orderlineitems.all():
				data = { orderlinefield.field.name: orderlinefield.value
									for orderlinefield in orderlineitem.orderlinefields.all() }
				data.update({
					'Email': order.owner.email,
					'Item':	orderline.item.name,
					'Quantity': orderline.quantity,
				})
				data_list.append(data)
		return data_list


	results = pd.DataFrame([ data for order in tqdm(orders.all(), desc='Processing orders...')
															 for data in _proccess_order(order) ])
	results.to_excel(_export_name("dump_sale", sale_pk))
	print("Dumped sale.")

def update_orders(sale_pk: int=None):
	"""
	Update all ongoing and awaiting orders
	"""

	payutc = Payutc({ 'app_key': PAYUTC_KEY })

	orders = Order.objects.prefetch_related('sale', 'sale__association', 'owner', 'orderlines', 'orderlines__item') \
												.filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value)

	if sale_pk is not None:
		orders = orders.filter(sale_id=sale_pk)

	def _check_payutc(order):
		transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
		return updateOrderStatus(order, transaction)

	def _process_order(order):
		from_status = order.status
		message = "Unchanged"

		if order.status == OrderStatus.ONGOING.value:
			# Check if the order is outdated
			if order.created_at + MAX_ONGOING_TIME < timezone.now():
				order.status = OrderStatus.EXPIRED.value
				order.save()
				message = "Outdated"

		elif order.status == OrderStatus.AWAITING_PAYMENT.value:
			transaction = payutc.getTransactionInfo({ 'tra_id': order.tra_id, 'fun_id': order.sale.association.fun_id })
			if 'error' in transaction:
				message = "Payutc Error: " + transaction['error']['message']
			else:
				updateOrderStatus(order, transaction)
				message = "Updated"

		return {
			'sale': order.sale.name,
			'owner': order.owner.email,
			'order_id': order.pk,
			'items': ', '.join('{} x {}'.format(orderline.quantity, orderline.item.name) for orderline in order.orderlines.all()),
			'from': OrderStatus(from_status).name,
			'to': OrderStatus(order.status).name,
			'message': message,
		}

	results = pd.DataFrame(_process_order(order) for order in tqdm(orders, desc="Updating orders..."))
	results.to_excel(_export_name("update_orders", sale_pk))
	print("Updated and dumped {} orders.".format(len(results)))

def gen_tickets(sale_pk: int=None):
	orders = Order.objects.prefetch_related('sale', 'sale__association', 'owner', 'orderlines', 'orderlines__orderlineitems', 'orderlines__item') \
												.annotate(nb_orderlineitems=Count('orderlines__orderlineitems')) \
												.filter(nb_orderlineitems=0, status=OrderStatus.PAID.value)

	if sale_pk is not None:
		orders = orders.filter(sale_id=sale_pk)

	results = []
	total_tickets = 0
	for order in tqdm(orders, desc="Generating tickets..."):
		before = sum(len(orderline.orderlineitems.all()) for orderline in order.orderlines.all())
		after = createOrderLineItemsAndFields(order)
		total_tickets += after
		results.append({
			'sale': order.sale.name,
			'owner': order.owner.email,
			'order_id': order.pk,
			'items': ', '.join('{} x {}'.format(orderline.quantity, orderline.item.name) for orderline in order.orderlines.all()),
			'quantity_before': before,
			'quantity_after': after,
		})

	results = pd.DataFrame(results)
	results.to_excel(_export_name("gen_tickets", sale_pk))
	print("Generated {} tickets for {} orders.".format(total_tickets, len(orders)))

def verify_orderlines(sale_pk: int=None):
	orders = Order.objects.prefetch_related('sale', 'owner', 'orderlines', 'orderlines__orderlineitems', 'orderlines__item') \
												.filter(status=OrderStatus.PAID.value)

	if sale_pk is not None:
		orders = orders.filter(sale_id=sale_pk)


	results = []
	# total_added = 0
	total_removed = 0
	changed_orders = 0
	for order in tqdm(orders, desc="Verifying orders..."):
		n_removed = 0
		removed_stats = []
		for orderline in order.orderlines.all():
			real_quantity = len(orderline.orderlineitems.all())

			# Delete the last overgiven tickets
			if orderline.quantity < real_quantity:
				n_removed += real_quantity - orderline.quantity
				for orderlineitem in orderline.orderlineitems.all()[orderline.quantity:]:
					removed_stats.append(orderlineitem.delete())
			# Create missing tickets
			# elif orderline.quantity > real_quantity:

		total_removed += n_removed
		changed_orders += int(n_removed > 0)
		results.append({
			'sale': order.sale.name,
			'owner': order.owner.email,
			'order_id': order.pk,
			'n_removed': n_removed,
			'removed': removed_stats,
		})

	results = pd.DataFrame(results)
	results.to_excel(_export_name("verify_orderlines", sale_pk))
	print("Verified {} orders and removed {} orderlineitems on {} orders.".format(len(orders), total_removed, changed_orders))
