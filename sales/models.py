from django.db import models
from authentication.models import User, UserType
from enum import Enum
from functools import reduce
import uuid


# ============================================
# 	Association & Member
# ============================================

class Association(models.Model):
	"""
	Represents the association information
	"""
	name 	= models.CharField(max_length=200)
	members = models.ManyToManyField(User, through='AssociationMember')
	fun_id 	= models.PositiveSmallIntegerField()			# TODO V2 : abstraire payment
	# bank_account = models.CharField(max_length=30)		# Why ?

	def __str__(self):
		return self.name

	class JSONAPIMeta:
		resource_name = "associations"

class AssociationMember(models.Model):
	"""
	Defines the link between Association and User
	"""
	user 		= models.ForeignKey(User, on_delete=models.CASCADE, related_name='associationmembers')
	association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='associationmembers')
	role 		= models.CharField(max_length=50)
	rights 		= models.CharField(max_length=50)

	def __str__(self):
		return "%s, %s @ %s" % (self.user, self.role, self.association)

	class Meta:
		verbose_name = "Association Member"			

	class JSONAPIMeta:
		resource_name = "associationmembers"


# ============================================
# 	Sale
# ============================================
		
class Sale(models.Model):
	"""
	Defines the Sale object
	"""
	# Description
	name 		= models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	association = models.ForeignKey(Association, on_delete=None, related_name='sales', editable=False)
	
	# Visibility
	is_active 	= models.BooleanField(default=True)
	public 		= models.BooleanField(default=True)

	# Timestamps
	created_at 	= models.DateTimeField(auto_now_add=True, editable=False)
	begin_at 	= models.DateTimeField()
	end_at 		= models.DateTimeField()

	max_item_quantity = models.IntegerField(null=True)
	max_payment_date  = models.DateTimeField()

	# TODO v2
	# paymentmethods = models.ManyToManyField(PaymentMethod)
	# payment_delay = models.DateTimeField()

	def __str__(self):
		return "%s par %s" % (self.name, self.association)

	class JSONAPIMeta:
		resource_name = "sales"


# ============================================
# 	Item
# ============================================

class ItemGroup(models.Model):
	name 	 = models.CharField(max_length = 200)
	quantity = models.IntegerField(null=True)
	max_per_user = models.IntegerField(null=True)		# TODO V2 : moteur de contraintes

	class JSONAPIMeta:
		resource_name = "itemgroups"

class Item(models.Model):
	"""
	Defines the Item object
	"""
	# Description
	name 		= models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	sale 		= models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	group 		= models.ForeignKey(ItemGroup, null=True, default=None, on_delete=models.SET_NULL, related_name='items')
	
	# Specification
	is_active 	= models.BooleanField(default=True)
	quantity 	= models.IntegerField(null=True)		# Null quand pas de restrinction sur l'item
	usertype 	= models.ForeignKey(UserType, on_delete=models.PROTECT)			# UserType ?
	price 		= models.FloatField()
	nemopay_id 	= models.CharField(max_length=30, null=True)		# TODO V2 : abstraire payment
	max_per_user = models.IntegerField(null=True)		# TODO V2 : moteur de contraintes

	fields 	= models.ManyToManyField('Field', through='ItemField', through_fields=('item','field')) #, related_name='fields')

	def quantity_left(self):
		if self.quantity == None:
			return None
		allOrders = self.sale.orders.filter(orderlines__item__pk=self.pk, status__in=OrderStatus.NOT_CANCELLED_LIST.value) \
						.prefetch_related('orderlines').all()
		allItemsBought = reduce(lambda acc, order: acc + \
				reduce(lambda acc2, orderline: acc2 + orderline.quantity, order.orderlines.all(), 0), \
			allOrders, 0)
		return self.quantity - allItemsBought

	class JSONAPIMeta:
		resource_name = "items"

# ============================================
# 	Order
# ============================================

class OrderStatus(Enum):
	ONGOING = 0
	AWAITING_VALIDATION = 1
	VALIDATED = 2
	NOT_PAID = 3
	PAID = 4
	EXPIRED = 5
	CANCELLED = 6

	CANCELLABLE_LIST = (NOT_PAID, AWAITING_VALIDATION)
	NOT_CANCELLED_LIST = (AWAITING_VALIDATION, VALIDATED, NOT_PAID, PAID) 
	BUYABLE_STATUS_LIST = (ONGOING, AWAITING_VALIDATION, NOT_PAID) 
	VALIDATED_LIST = (VALIDATED, PAID)

	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)

class Order(models.Model):
	"""
	Defines the Order object
	"""
	owner 	= models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', editable=False)
	sale 	= models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='orders', editable=False)

	created_at = models.DateTimeField(auto_now_add = True, editable=False)
	updated_at = models.DateTimeField(auto_now_add = True)

	# status = models.OrderStatus()
	status = models.PositiveSmallIntegerField(
		choices = OrderStatus.choices(),  # Choices is a list of Tuple
		default = OrderStatus.ONGOING.value
	)
	tra_id = models.IntegerField(null = True, default = None)

	class JSONAPIMeta:
		resource_name = "orders"


class OrderLine(models.Model):
	"""
	Defines the link between an Order and an Item
	"""
	item 	 = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orderlines', editable=False)
	order 	 = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderlines', editable=False)
	quantity = models.IntegerField()

	class JSONAPIMeta:
		resource_name = "orderlines"


# ============================================
# 	Field
# ============================================


class Field(models.Model):
	"""
	Defines the Field object
	"""
	name 	= models.CharField(max_length=200)
	type 	= models.CharField(max_length=200)
	default = models.CharField(max_length=200, null=True)
	items 	= models.ManyToManyField(Item, through='ItemField', through_fields=('field','item'))

	class JSONAPIMeta:
		resource_name = "fields"

class ItemField(models.Model):
	"""
	Defines the ItemField object
	"""
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='itemfields', editable=False)
	item  = models.ForeignKey(Item,  on_delete=models.CASCADE, related_name='itemfields', editable=False)
	editable = models.BooleanField(default=True)

	# sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	# itemgroup = models.ForeignKey(ItemGroup, on_delete = None, related_name = 'itemgroups')
	# usertype = models.ManyToManyField('authentication.UserType')

	class JSONAPIMeta:
		resource_name = "itemfields"


class OrderLineItem(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	orderline = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name="orderlineitems", editable=False)

	class JSONAPIMeta:
		resource_name = "orderlineitems"

class OrderLineField(models.Model):
	"""
	Defines the OrderLineField object
	"""
	orderlineitem = models.ForeignKey(OrderLineItem, on_delete=models.CASCADE, related_name='orderlinefields', editable=False)
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='orderlinefields', editable=False)
	value = models.CharField(max_length=1000, null = True, editable='isEditable') # TODO ??

	def isEditable(self):
		itemfield = ItemField.objects.get(field__pk=self.field.pk, item__pk=self.orderlineitem.orderline.item.pk)
		return itemfield.editable

	class JSONAPIMeta:
		resource_name = "orderlinefields"

