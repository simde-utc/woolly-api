from django.db import models
from core.models import ApiModel
from authentication.models import User, UserType
from enum import Enum
import uuid


# ============================================
# 	Association
# ============================================

class Association(ApiModel):
	"""
	Defines an Association
	"""
	id = models.UUIDField(primary_key=True, editable=False)
	shortname = models.CharField(max_length=200)
	fun_id    = models.PositiveSmallIntegerField(null=True, blank=True)			# TODO V2 : abstraire payment

	@classmethod
	def get_api_endpoint(cls, **params) -> str:
		url = []
		url.append('assos')
		if 'pk' in params:
			url.append(self.pk_to_url(params['pk']))
		return '/'.join(url)

	def __str__(self):
		return self.shortname

class Sale(models.Model):
	"""
	Defines a Sale
	"""
	# Description
	# slud
	name        = models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	association = models.ForeignKey(Association, on_delete=None, related_name='sales') # editable=False
	# cgv = TODO
	
	# Visibility
	is_active   = models.BooleanField(default=True)
	public      = models.BooleanField(default=True)

	# Timestamps
	created_at  = models.DateTimeField(auto_now_add=True, editable=False)
	begin_at    = models.DateTimeField()
	end_at      = models.DateTimeField()

	max_item_quantity = models.PositiveIntegerField(blank=True, null=True)
	max_payment_date  = models.DateTimeField() # TODO

	# TODO v2
	# paymentmethods = models.ManyToManyField(PaymentMethod)

	def __str__(self):
		return "%s par %s" % (self.name, self.association)


# ============================================
# 	Item
# ============================================

class ItemGroup(models.Model):
	"""
	Gathers items under a common group
	for better display or management
	"""
	name 	 = models.CharField(max_length = 200)
	quantity = models.PositiveIntegerField(blank=True, null=True)
	max_per_user = models.PositiveIntegerField(blank=True, null=True)		# TODO V2 : moteur de contraintes
	# sale 		 = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')

	def __str__(self):
		return self.name

class Item(models.Model):
	"""
	Defines a sellable Item
	"""
	# Description
	name 		= models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	sale 		= models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	group 		= models.ForeignKey(ItemGroup, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='items')
	
	# Specification
	is_active 	= models.BooleanField(default=True)
	quantity 	= models.PositiveIntegerField(blank=True, null=True)		# Null quand pas de restrinction sur l'item
	usertype 	= models.ForeignKey(UserType, on_delete=models.PROTECT)			# UserType ?
	price 		= models.FloatField()
	nemopay_id 	= models.CharField(max_length=30, blank=True, null=True)		# TODO V2 : abstraire payment
	max_per_user = models.PositiveIntegerField(blank=True, null=True)		# TODO V2 : moteur de contraintes

	fields 	= models.ManyToManyField('Field', through='ItemField', through_fields=('item','field')) #, related_name='fields')

	def quantity_left(self):
		if self.quantity == None:
			return None
		allOrders = self.sale.orders.filter(orderlines__item__pk=self.pk, status__in=OrderStatus.NOT_CANCELLED_LIST.value) \
						.prefetch_related('orderlines').all()
		allItemsBought = sum(orderline.quantity for order in allOrders
																						for orderline in order.orderlines.filter(item=self).all())
		return self.quantity - allItemsBought

	def __str__(self):
		return "%s (%s)" % (self.name, self.sale)

	class Meta:
		ordering = ('id',)


# ============================================
# 	Order
# ============================================

class OrderStatus(Enum):
	"""
	Possible status of an Order
	"""
	ONGOING = 0
	AWAITING_VALIDATION = 1
	VALIDATED = 2
	NOT_PAID = 3 # TODO AWAITING_PAYMENT
	PAID = 4
	EXPIRED = 5
	CANCELLED = 6

	# Helpers, not real choices
	CANCELLABLE_LIST = (NOT_PAID, AWAITING_VALIDATION)
	# NOT_CANCELLED_LIST = (AWAITING_VALIDATION, VALIDATED, NOT_PAID, PAID) 
	NOT_CANCELLED_LIST = (PAID, VALIDATED) 
	BUYABLE_STATUS_LIST = (ONGOING, AWAITING_VALIDATION, NOT_PAID)  # TODO PENDING_LIST
	VALIDATED_LIST = (VALIDATED, PAID)
	CANCELLED_LIST = (EXPIRED, CANCELLED)

	# Used for Django choices, return only choices whose value is int
	@classmethod
	def choices(cls):
		return tuple((i.value, i.name) for i in cls if isinstance(i.value, int))

class Order(models.Model):
	"""
	Defines the Order object
	"""
	owner 	= models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', editable=False)
	sale 		= models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='orders', editable=False)

	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True)

	status = models.PositiveSmallIntegerField(
		choices=OrderStatus.choices(),	# Choices is a list of Tuple
		default=OrderStatus.ONGOING.value,
	)
	tra_id = models.IntegerField(blank=True, null=True, default=None)

	def __str__(self):
		return "%d %s - %s ordered by %s" % (self.id, OrderStatus(self.status).name, self.sale, self.owner)

	class Meta:
		ordering = ('id',)

class OrderLine(models.Model):
	"""
	Links an Order to an Item with a quantity
	"""
	item 	 = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orderlines') #, editable=False)
	order 	 = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderlines') #, editable=False)
	quantity = models.IntegerField()

	def __str__(self):
		return "%s - %dx %s (Order %s)" % (self.id, self.quantity, self.item.name, self.order)

	class Meta:
		ordering = ('id',)

class OrderLineItem(models.Model):
	"""
	Represents a single OrderLine.item with a unique id for ticketing
	May have specifications with related OrderLineFields
	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	orderline = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name="orderlineitems")

	def __str__(self):
		return "%s - %s" % (self.id, self.orderline)

	class Meta:
		ordering = ('id',)


# ============================================
# 	Field
# ============================================

class Field(models.Model):
	"""
	Defines an Item's specification
	"""
	name 	= models.CharField(max_length=200)
	type 	= models.CharField(max_length=200)
	default = models.CharField(max_length=200, blank=True, null=True)
	items 	= models.ManyToManyField(Item, through='ItemField', through_fields=('field','item'))

	def __str__(self):
		return "%s (%s)" % (self.name, self.type)

	class Meta:
		ordering = ('id',)

class ItemField(models.Model):
	"""
	Links an Item to a Field with additionnal options
	"""
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='itemfields') #, editable=False)
	item  = models.ForeignKey(Item,  on_delete=models.CASCADE, related_name='itemfields') #, editable=False)
	# Options
	editable = models.BooleanField(default=True)

	# sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	# itemgroup = models.ForeignKey(ItemGroup, on_delete = None, related_name = 'itemgroups')
	# usertype = models.ManyToManyField('authentication.UserType')

	def __str__(self):
		return "%s - %s)" % (self.item, self.field)

	class Meta:
		ordering = ('id',)

class OrderLineField(models.Model):
	"""
	Specifies the Field value taken by the OrderLine Item
	"""
	orderlineitem = models.ForeignKey(OrderLineItem, on_delete=models.CASCADE, related_name='orderlinefields')
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='orderlinefields')
	value = models.CharField(max_length=1000, blank=True, null= True, editable='isEditable') # TODO Working ??

	def isEditable(self) -> bool:
		itemfield = ItemField.objects.get(field__pk=self.field.pk, item__pk=self.orderlineitem.orderline.item.pk)
		return itemfield.editable

	def __str__(self):
		return "%s - %s = %s" % (self.orderlineitem.id, self.field.name, self.value)

	class Meta:
		ordering = ('id',)

