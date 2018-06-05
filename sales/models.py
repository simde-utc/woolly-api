from django.db import models
from authentication.models import User, UserType
from enum import Enum

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

	class JSONAPIMeta:
		resource_name = "associationmembers"


# ============================================
# 	Sale
# ============================================

class PaymentMethod(models.Model):
	# TODO à mettre à part, inutile pour la beta
	name 	= models.CharField(max_length = 50)
	api_url = models.CharField(max_length = 500)

	class JSONAPIMeta:
		resource_name = "paymentmethods"
		
class Sale(models.Model):
	"""
	Defines the Sale object
	"""
	# Description
	name 		= models.CharField(max_length = 200)
	description = models.CharField(max_length = 1000)
	association = models.ForeignKey(Association, on_delete=None, related_name='sales')
	
	# Timestamps & Controls
	is_active 	= models.BooleanField(default=True)
	created_at 	= models.DateTimeField(auto_now_add=True)
	begin_at 	= models.DateTimeField()
	end_at 		= models.DateTimeField()

	max_item_quantity = models.IntegerField(null = True)
	max_payment_date  = models.DateTimeField()

	# TODO v2
	# paymentmethods = models.ManyToManyField(PaymentMethod)
	# payment_delay = models.DateTimeField()

	class JSONAPIMeta:
		resource_name = "sales"


# ============================================
# 	Item
# ============================================

class ItemGroup(models.Model):
	name 	 = models.CharField(max_length = 200)
	quantity = models.IntegerField(default=True)

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
	quantity 	= models.IntegerField(null=True)		# Null quand pas de restrinction sur l'item
	usertype 	= models.ForeignKey(UserType, on_delete=models.PROTECT)			# UserType ?
	price 		= models.FloatField()
	nemopay_id 	= models.CharField(max_length=30, null=True)		# TODO V2 : abstraire payment
	max_per_user = models.IntegerField(null=True)		# TODO V2 : moteur de contraintes

	class JSONAPIMeta:
		resource_name = "items"

# ============================================
# 	Order
# ============================================

class OrderStatus(Enum):
	ONGOING = 0
	AWAITING_VALIDATION = 1
	VALIDATED = 2
	NOT_PAYED = 3
	PAYED = 4
	EXPIRED = 5
	CANCELLED = 6

	@classmethod
	def choices(cls):
		return tuple((i.name, i.value) for i in cls)

class Order(models.Model):
	"""
	Defines the Order object
	"""
	owner 	= models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
	sale 	= models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='orders')

	created_at = models.DateTimeField(auto_now_add = True)
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
	item 	 = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orderlines')
	order 	 = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderlines')
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
	type 	= models.CharField(max_length=1000)
	default = models.CharField(max_length=200)
	items 	= models.ManyToManyField(Item, through='ItemField') #, related_name='fields')

	class JSONAPIMeta:
		resource_name = "fields"


class ItemField(models.Model):
	"""
	Defines the ItemField object
	"""
	editable = models.BooleanField(default=True)
	item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='itemfields')
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='itemfields')

	# sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	# itemgroup = models.ForeignKey(ItemGroup, on_delete = None, related_name = 'itemgroups')
	# usertype = models.ManyToManyField('authentication.UserType')

	class JSONAPIMeta:
		resource_name = "itemfields"


class OrderLineField(models.Model):
	"""
	Defines the OrderLineField object
	"""
	value = models.CharField(max_length=1000)
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="orderlinesfields")
	orderline = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name="orderlinesfields")

	class JSONAPIMeta:
		resource_name = "orderlinefields"

