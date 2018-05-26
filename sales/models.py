from django.db import models
from authentication.models import User, UserType

# ============================================
# 	Associations & Members
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
# 	Ventes
# ============================================

class Sale(models.Model):
	"""
	Defines the Sale object
	"""
	# Description
	name 		= models.CharField(max_length = 200)
	description = models.CharField(max_length = 1000)
	association = models.ForeignKey(Association, on_delete=None, related_name='sales', blank=True)
	
	# Timestamps & Controls
	is_active 	= models.BooleanField(default = True)
	created_at 	= models.DateTimeField(auto_now_add = True)
	begin_at 	= models.DateTimeField()
	end_at 		= models.DateTimeField()

	max_payment_date = models.DateTimeField()
	max_item_quantity = models.IntegerField()

	# TODO v2
	# paymentmethods = models.ManyToManyField(PaymentMethod)
	# payment_delay = models.DateTimeField()

	class JSONAPIMeta:
		resource_name = "sales"



# ============================================
# 	Orders and Items
# ============================================

class ItemGroup(models.Model):
	name 	= models.CharField(max_length = 200)

	class JSONAPIMeta:
		resource_name = "itemgroups"


class Item(models.Model):
	"""
	Defines the Item object
	"""
	# Description
	name 		= models.CharField(max_length = 200)
	description = models.CharField(max_length = 1000)
	sale 		= models.ForeignKey(Sale, related_name='items')
	group 		= models.ForeignKey(ItemGroup, related_name='items')
	
	# Specification
	quantity 	= models.IntegerField()
	usertype 	= models.ForeignKey(UserType)			# UserType ?
	price 		= models.FloatField()
	nemopay_id  = models.CharField(max_length = 30)		# TODO V2 : abstraire payment

	class JSONAPIMeta:
		resource_name = "items"


class Order(models.Model):
	"""
	Defines the Order object
	"""
	status 	= models.CharField(max_length = 50)
	owner 	= models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
	sale 	= models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='orders')

	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField()

	class JSONAPIMeta:
		resource_name = "orders"


class OrderLine(models.Model):
	"""
	Defines the link between an Order and an Item
	"""
	item 		= models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orderlines')
	order 		= models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderlines')
	quantity 	= models.IntegerField()

	class JSONAPIMeta:
		resource_name = "orderlines"



# ============================================
# 	Fields
# ============================================


class Field(models.Model):
	"""
	Defines the Field object
	"""
	name 	= models.CharField(max_length = 200)
	type 	= models.CharField(max_length = 1000)
	default = models.CharField(max_length = 200)

	item 	= models.ManyToManyField(Item, through='ItemField')
	orderline = models.ManyToManyField(OrderLine, through='OrderLineField')

	class JSONAPIMeta:
		resource_name = "fields"


class ItemField(models.Model):
	"""
	Defines the ItemField object
	"""
	editable = models.BooleanField(default = True)

	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	itemgroup = models.ForeignKey(ItemGroup, on_delete = None, related_name = 'itemgroups')
	usertype = models.ManyToManyField('authentication.UserType')
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	# item = models.ManyToManyField(Item, through='ItemField')
	field = models.ForeignKey(Field, on_delete=models.CASCADE)

	class JSONAPIMeta:
		resource_name = "itemfields"

class OrderLineField(models.Model):
	"""
	Defines the OrderLineField object
	"""
	value = models.CharField(max_length=1000)
	orderline = models.ForeignKey(OrderLine, on_delete=models.CASCADE)
	field = models.ForeignKey(Field, on_delete=models.CASCADE)

	class JSONAPIMeta:
		resource_name = "orderlinefields"
