from django.db import models
from django.conf import settings


# ============================================
# 	Associations
# ============================================

class Association(models.Model):
	"""
	Represents the association information
	"""
	name = models.CharField(max_length=200)
	bank_account = models.CharField(max_length=30)
	# The foundation ID is used to  link the app to NemoPay
	# No calculations are going to be made with it
	# So it's a char field
	foundation_id = models.CharField(max_length=30)
	members = models.ManyToManyField(settings.AUTH_USER_MODEL)

	class JSONAPIMeta:
		resource_name = "associations"

class AssociationMember(models.Model):
	"""
	Defines the link between Association and User
	"""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='associationmembers')
	association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='associationmembers')
	role = models.CharField(max_length=50)
	rights = models.CharField(max_length=50)

	class JSONAPIMeta:
		resource_name = "associationmembers"


# ============================================
# 	Ventes & Paiements
# ============================================

class PaymentMethod(models.Model):
	"""Define the payment options"""
	name = models.CharField(max_length=200)
	api_url = models.CharField(max_length=500, blank=True)

	class JSONAPIMeta:
		resource_name = "paymentmethods"


class Sale(models.Model):
	"""
	Defines the Sale object
	"""
	name = models.CharField(max_length = 200)
	description = models.CharField(max_length = 1000)
	creation_date = models.DateTimeField(auto_now_add = True)
	begin_date = models.DateTimeField()
	end_date = models.DateTimeField()
	max_payment_date = models.DateTimeField()
	# payment_delay = models.DateTimeField()
	max_item_quantity = models.IntegerField()
	# is_active = models.BooleanField(default = True)

	paymentmethods = models.ManyToManyField(PaymentMethod)

	association = models.ForeignKey(Association, on_delete=None, related_name='sales', blank=True)

	class JSONAPIMeta:
		resource_name = "sales"


# ============================================
# 	Orders and Items
# ============================================

class Order(models.Model):
	"""
	Defines the Order object
	"""
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		related_name='orders',
		on_delete=models.CASCADE
	)

	status = models.CharField(max_length=50)
	date = models.DateTimeField()
	price = models.FloatField()
	hash_key = models.CharField(max_length=50)
	sale = models.ForeignKey(Sale, on_delete = models.CASCADE, related_name='sale')


	class JSONAPIMeta:
		resource_name = "orders"


class ItemGroup(models.Model):
	"""
	Defines the ItemGroup object
	"""
	name = models.CharField(max_length=200)
	quantity = models.IntegerField()

	class JSONAPIMeta:
		resource_name = "itemgroups"

class Item(models.Model):
	"""
	Defines the Item object
	"""
	name = models.CharField(max_length = 200)
	description = models.CharField(max_length = 1000)
	quantity = models.IntegerField()
	price = models.FloatField()

	sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	itemgroup = models.ForeignKey(ItemGroup, on_delete = None, related_name = 'itemgroups')
	usertype = models.ManyToManyField('authentication.UserType')

	nemopay_id = models.CharField(max_length = 30)

	class JSONAPIMeta:
		resource_name = "items"


class OrderLine(models.Model):
	"""
	Defines the link between an Order and an Item
	"""
	item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orderlines')
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderlines')
	quantity = models.IntegerField()

	class JSONAPIMeta:
		resource_name = "orderlines"


# ============================================
# 	Fields
# ============================================

class Field(models.Model):
	"""
	Defines the Field object
	"""
	name = models.CharField(max_length = 200) # TODO Unique ?
	type = models.CharField(max_length = 1000)
	default = models.CharField(max_length = 255)

	item = models.ManyToManyField(Item, through='ItemField')

	orderline = models.ManyToManyField(OrderLine, through='OrderLineField')

	class JSONAPIMeta:
		resource_name = "fields"


class ItemField(models.Model):
	"""
	Defines the ItemField object
	"""
	editable = models.BooleanField(default = True)

	item = models.ForeignKey(Item, on_delete=models.CASCADE)
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
