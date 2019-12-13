from authentication.models import User, UserType
from core.models import ApiModel
from django.db import models
from enum import Enum
import uuid

from django.db import transaction
from django.core.mail import EmailMessage

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
	# TODO Fetch fun_id

	@classmethod
	def get_api_endpoint(cls, params: dict) -> str:
		url = 'assos'
		if 'pk' in params:
			url += cls.pk_to_url(params['pk'])
		if 'user_pk' in params:
			url = f"users/{params['user_pk']}/{url}"
		return url

	def __str__(self) -> str:
		return self.shortname

class Sale(models.Model):
	"""
	Defines a Sale
	"""
	# Description
	# slug        = models.CharField(max_length=200, unique=True)
	name        = models.CharField(max_length=200)
	description = models.CharField(max_length=1000, blank=True)
	association = models.ForeignKey(Association, on_delete=None, related_name='sales') #, editable=False)
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

	def __str__(self) -> str:
		return "%s par %s" % (self.name, self.association)

	class Meta:
		ordering = ('-created_at',)

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

	def __str__(self) -> str:
		return self.name

class Item(models.Model):
	"""
	Defines a sellable Item
	"""
	# Description
	name        = models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	sale        = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	group       = models.ForeignKey(ItemGroup, blank=True, null=True, default=None, on_delete=models.SET_NULL, related_name='items')
	
	# Specifications
	is_active    = models.BooleanField(default=True)
	quantity     = models.IntegerField(blank=True, null=True)		# Null quand pas de restrinction sur l'item
	max_per_user = models.IntegerField(blank=True, null=True)		# TODO V2 : moteur de contraintes
	usertype     = models.ForeignKey(UserType, on_delete=models.PROTECT)
	price        = models.FloatField()
	nemopay_id   = models.CharField(max_length=30, blank=True, null=True)		# TODO V2 : abstraire payment

	fields = models.ManyToManyField('Field', through='ItemField', through_fields=('item','field')) #, related_name='fields')

	def quantity_left(self):
		if self.quantity == None:
			return None
		allOrders = self.sale.orders.filter(orderlines__item__pk=self.pk, status__in=OrderStatus.BOOKED_LIST.value) \
						.prefetch_related('orderlines').all()
		allItemsBought = sum(orderline.quantity for order in allOrders
																						for orderline in order.orderlines.filter(item=self).all())
		return self.quantity - allItemsBought

	def __str__(self) -> str:
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
	AWAITING_PAYMENT = 3
	PAID = 4
	EXPIRED = 5
	CANCELLED = 6

	# ====== Helpers, not real choices ======

	# Orders which can be bought
	BUYABLE_STATUS_LIST = (ONGOING, AWAITING_VALIDATION, AWAITING_PAYMENT)
	# Orders which book items, temporary or not 
	BOOKED_LIST = (AWAITING_VALIDATION, VALIDATED, AWAITING_PAYMENT, PAID)
	# Orders that are definitely valid
	VALIDATED_LIST = (VALIDATED, PAID)
	# Orders which can be cancelled
	CANCELLABLE_LIST = (AWAITING_PAYMENT, AWAITING_VALIDATION)
	# Orders which are definitely cancelled
	CANCELLED_LIST = (EXPIRED, CANCELLED)

	MESSAGES = {
		ONGOING: "Votre commande est en cours",
		AWAITING_PAYMENT: "Votre commande en attente de paiement",
		AWAITING_VALIDATION: "Votre commande en attente de validation",
		PAID: "Votre commande est payée",
		VALIDATED: "Votre commande est validée",
		EXPIRED: "Votre commande est expirée",
		CANCELLED: "Votre commande a été annulée",
	}

	@classmethod
	def choices(cls):
		"""
		Used for Django choices
		Return only real choices and not list of choices
		"""
		return tuple((i.value, i.name) for i in cls if isinstance(i.value, int))

class Order(models.Model):
	"""
	Defines the Order object
	This is the central model of all the project
	"""
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')#, editable=False)
	sale  = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='orders')#, editable=False)

	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_at = models.DateTimeField(auto_now=True)

	status = models.PositiveSmallIntegerField(
		choices=OrderStatus.choices(),
		default=OrderStatus.ONGOING.value,
	)
	tra_id = models.IntegerField(blank=True, null=True, default=None)

	# Additional methods

	def update_status(self, status: OrderStatus) -> dict:
		"""
		Update the order status, make side changes if needed,
		and return an update response
		"""
		resp = {
			'old_status': self.get_status_display(),
			# Do not update if same status, booked or cancelled orders
			'updated': not (self.status == status.value
			                or self.status in OrderStatus.BOOKED_LIST.value
			                or self.status == OrderStatus.CANCELLED.value),
			# Redirect to payment if needed
			'redirect_to_payment': status.value == OrderStatus.AWAITING_PAYMENT.value,
			# If sale freshly validated, generate tickets
			'tickets_generated': (self.status not in OrderStatus.VALIDATED_LIST.value
			                      and status.value in OrderStatus.VALIDATED_LIST.value),
		}

		# Update order status
		if resp['updated']:
			self.status = status.value
			self.save()

		# Generate tickets if needed
		if resp['tickets_generated']:
			self.create_orderlineitems_and_fields()

		resp['status']  = self.get_status_display()
		resp['message'] = OrderStatus.MESSAGES.value[self.status.value]
		return resp

	@transaction.atomic
	def create_orderlineitems_and_fields(self) -> int:
		"""
		When an order has just been validated, create
		all the orderlineitems and fields required
		TODO : add a lock or something, and improve from scripts
		"""
		from .serializers import OrderLineItemSerializer, OrderLineFieldSerializer
		orderlines = self.orderlines.filter(quantity__gt=0) \
		                 .prefetch_related('item', 'orderlineitems')

		total = 0
		for orderline in orderlines.all():
			qte = orderline.quantity - len(orderline.orderlineitems.all())
			while qte > 0:
				# Create OrderLineItem 
				orderlineitem = OrderLineItemSerializer(data={
					'orderline': orderline.id
				})
				orderlineitem.is_valid(raise_exception=True)
				orderlineitem.save()

				# Create OrderLineFields
				for field in orderline.item.fields.all():
					orderlinefield = OrderLineFieldSerializer(data = {
						'orderlineitem': orderlineitem.data['id'],
						'field': field.id,
						'value': get_field_default_value(field.default, self),
					})
					orderlinefield.is_valid(raise_exception=True)
					orderlinefield.save()
					
				total += 1
				qte -= 1
				
		return total

	def send_confirmation_mail(self):
		"""
		Send a confirmation mail to the owner of the order
		"""
		if self.status not in OrderStatus.VALIDATED_LIST.value:
			raise Exception(f"The order must be valid to send a confirmation mail")

		# TODO : généraliser + markdown
		link_order = "http://assos.utc.fr/picasso/degustations/commandes/" + str(self.pk)
		message = "Bonjour " + self.owner.get_full_name() + ",\n\n" \
						+ "Votre commande n°" + str(self.pk) + " vient d'être confirmée.\n" \
						+ "Vous avez commandé:\n" \
						+ "".join([ " - " + str(ol.quantity) + " " + ol.item.name + "\n" for ol in self.orderlines.all() ]) \
						+ "Vous pouvez télécharger vos billets ici : " + link_order + "\n\n" \
						+ "Merci d'avoir utilisé Woolly"

		email = EmailMessage(
			subject="Woolly - Confirmation de commande",
			body=message,
			from_email="woolly@assos.utc.fr",
			to=[self.owner.email],
			reply_to=["woolly@assos.utc.fr"],
		)
		return email.send()

	def __str__(self) -> str:
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

	def __str__(self) -> str:
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

	def __str__(self) -> str:
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

	def __str__(self) -> str:
		return "%s (%s)" % (self.name, self.type)

	class Meta:
		ordering = ('id',)

class ItemField(models.Model):
	"""
	Links an Item to a Field with additionnal options
	"""
	field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='itemfields') #, editable=False)
	item  = models.ForeignKey(Item,  on_delete=models.CASCADE, related_name='itemfields') #, editable=False)
	editable = models.BooleanField(default=True)

	# sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
	# itemgroup = models.ForeignKey(ItemGroup, on_delete = None, related_name = 'itemgroups')

	def __str__(self) -> str:
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

	def __str__(self) -> str:
		return "%s - %s = %s" % (self.orderlineitem.id, self.field.name, self.value)

	class Meta:
		ordering = ('id',)

