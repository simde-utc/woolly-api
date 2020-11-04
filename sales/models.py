import uuid
from enum import Enum

from django.conf import settings
from django.utils import timezone
from django.db import models, transaction
from django.core.mail import EmailMessage

from core.models import APIModel
from core.helpers import get_field_default_value
from authentication.models import User, UserType

NAME_FIELD_MAXLEN = 150
DESC_FIELD_MAXLEN = 512
URL_FIELD_MAXLEN = 254


# --------------------------------------------
#   Associations
# --------------------------------------------

class Association(APIModel):
    """
    Defines an Association
    """
    id = models.UUIDField(primary_key=True, editable=False)
    shortname = models.CharField(max_length=NAME_FIELD_MAXLEN)
    fun_id    = models.PositiveSmallIntegerField(null=True, blank=True)
    # TODO Abstraire payment

    @classmethod
    def get_api_endpoint(cls, params: dict) -> str:
        url = 'assos'
        if 'pk' in params:
            url += cls.pk_to_url(params['pk'])

        # TODO Ask for specific roles in associations
        if 'user_pk' in params:
            # Don't filter association if user is admin
            user_is_admin = User.objects.values_list('is_admin', flat=True) \
                                        .get(pk=params['user_pk'])
            if not user_is_admin:
                url = f"users/{params['user_pk']}/{url}"
        return url

    def __str__(self) -> str:
        return self.shortname

    class Meta:
        ordering = ('shortname',)


class Sale(models.Model):
    """
    Defines a Sale
    """
    # Description
    id          = models.SlugField(primary_key=True, max_length=64, blank=False)
    name        = models.CharField(max_length=NAME_FIELD_MAXLEN)
    description = models.CharField(max_length=DESC_FIELD_MAXLEN, blank=True)
    association = models.ForeignKey(Association, on_delete=models.DO_NOTHING, related_name='sales')

    # Visibility
    is_active   = models.BooleanField(default=True)
    is_public   = models.BooleanField(default=True)

    # Timestamps
    created_at  = models.DateTimeField(auto_now_add=True, editable=False)
    begin_at    = models.DateTimeField()
    end_at      = models.DateTimeField()

    max_item_quantity = models.PositiveIntegerField(blank=True, null=True)

    # Customization
    cgv   = models.URLField(max_length=URL_FIELD_MAXLEN, blank=True, null=True)
    image = models.URLField(max_length=URL_FIELD_MAXLEN, blank=True, null=True)
    color = models.CharField(max_length=6, blank=True, null=True)

    # TODO mail_template tickets
    # TODO paymentmethods = models.ManyToManyField(PaymentMethod)

    def __str__(self) -> str:
        return f"{self.name} par {self.association}"

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=('-created_at',)),
        ]


# --------------------------------------------
#   Items
# --------------------------------------------

class ItemGroup(models.Model):
    """
    Gathers items under a common group
    for better display or validation
    """
    name         = models.CharField(max_length=NAME_FIELD_MAXLEN)
    description  = models.CharField(max_length=DESC_FIELD_MAXLEN, blank=True)
    sale         = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='itemgroups')

    is_active    = models.BooleanField(default=True)
    quantity     = models.PositiveIntegerField(blank=True, null=True)
    max_per_user = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    """
    Defines a sellable Item
    """
    # Description
    name        = models.CharField(max_length=NAME_FIELD_MAXLEN)
    description = models.CharField(max_length=DESC_FIELD_MAXLEN, blank=True)
    sale        = models.ForeignKey(Sale,
                                    on_delete=models.CASCADE,
                                    related_name='items')
    group       = models.ForeignKey(ItemGroup,
                                    blank=True, null=True, default=None,
                                    on_delete=models.SET_NULL, related_name='items')

    # Specifications
    usertype     = models.ForeignKey(UserType, on_delete=models.PROTECT)
    quantity     = models.PositiveSmallIntegerField(blank=True, null=True)
    max_per_user = models.PositiveSmallIntegerField(blank=True, null=True)
    is_active    = models.BooleanField(default=True)
    price        = models.FloatField()

    # Payment
    nemopay_id   = models.CharField(max_length=30, blank=True, null=True)
    # TODO Abstraire payment

    fields = models.ManyToManyField('Field',
                                    through='ItemField',
                                    through_fields=('item', 'field'))

    def quantity_sold(self) -> int:
        """
        Count item quantity sold
        """
        filters = {
            'sale': self.sale_id,
            'orderlines__item__pk': self.pk,
            'status__in': OrderStatus.BOOKING_LIST.value,
        }

        qt_sum = models.Sum('orderlines__quantity',
                            filter=models.Q(orderlines__item__pk=self.pk))
        return (
            Order.objects.filter(**filters)
            .annotate(orderline_quantity=qt_sum)
            .aggregate(sum=models.Sum('orderline_quantity'))
        )['sum'] or 0

    def quantity_left(self) -> int:
        """
        Get quantity left
        """
        if self.quantity is None:
            return None
        return self.quantity - self.quantity_sold()

    def quantity_estimation(self) -> int:
        """
        Quantity estimation for client UI x/3
        """
        if self.quantity is None:
            return None
        percent = self.quantity_sold() / self.quantity
        if percent > 0.45:
            return 3
        elif percent > 0.2:
            return 2
        elif percent > 0:
            return 1
        else:
            return 0

    def save(self, *args, **kwargs) -> None:
        """
        Save item and synch it with the payment system
        """
        from payment.helpers import get_pay_service
        pay_service = get_pay_service(self)
        pay_service.sync_item(self)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.sale})"

    class Meta:
        ordering = ('id',)


# --------------------------------------------
#   Orders
# --------------------------------------------

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
    BOOKING_LIST = (AWAITING_VALIDATION, VALIDATED, AWAITING_PAYMENT, PAID)
    # Orders that are definitely valid
    VALIDATED_LIST = (VALIDATED, PAID)
    # Orders which are definitely cancelled
    CANCELLED_LIST = (EXPIRED, CANCELLED)
    # Orders that are not in a stable state
    AWAITING_LIST = (AWAITING_PAYMENT, AWAITING_VALIDATION)
    # Orders which can be cancelled
    CANCELLABLE_LIST = AWAITING_LIST
    # Orders that are not supposed to be updated
    STABLE_LIST = (PAID, VALIDATED, EXPIRED, CANCELLED)

    MESSAGES = {
        ONGOING: "Votre commande est en cours",
        AWAITING_PAYMENT: "Votre commande est en attente de paiement",
        AWAITING_VALIDATION: "Votre commande est en attente de validation",
        PAID: "Votre commande est payée",
        VALIDATED: "Votre commande est validée",
        EXPIRED: "Votre commande est expirée",
        CANCELLED: "Votre commande a été annulée",
    }

    @classmethod
    def choices(cls) -> tuple:
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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', editable=False)
    sale  = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='orders', editable=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.PositiveSmallIntegerField(
        choices=OrderStatus.choices(),
        default=OrderStatus.ONGOING.value,
    )
    # TODO Abstraire payment
    tra_id = models.IntegerField(blank=True, null=True, default=None)

    # ----- Additional methods

    def is_expired(self) -> bool:
        """
        Check expiracy time according to order status and expire if needed
        """
        if self.status == OrderStatus.EXPIRED.value:
            return True

        if self.status in OrderStatus.STABLE_LIST.value:
            return False

        delta = timezone.now() - self.created_at
        return any((
            self.status == OrderStatus.ONGOING.value and delta > settings.MAX_ONGOING_TIME,
            self.status == OrderStatus.AWAITING_PAYMENT.value and delta > settings.MAX_PAYMENT_TIME,
            self.status == OrderStatus.AWAITING_VALIDATION.value and delta > settings.MAX_VALIDATION_TIME,
        ))

    def fetch_status(self) -> OrderStatus:
        """
        Fetch the status from external APIs if needed, doesn't update it !
        """
        if self.status in OrderStatus.STABLE_LIST.value:
            return OrderStatus(self.status)

        # Check payment status if waiting
        if self.status == OrderStatus.AWAITING_PAYMENT.value:
            from payment.helpers import get_pay_service
            return get_pay_service(self).get_transaction_status(self)

        if self.is_expired():
            return OrderStatus.EXPIRED

        return OrderStatus(self.status)

    def update_status(self, status: OrderStatus=None) -> dict:
        """
        Update the order status, make side changes if needed,
        and return an update response
        """
        if status is None:
            status = self.fetch_status()

        resp = {
            'old_status': self.get_status_display(),
            # Do not update if same or stable status
            'updated': self.status != status.value and self.status not in OrderStatus.STABLE_LIST.value,
            # Redirect to payment if needed
            'redirect_to_payment': status and status.value == OrderStatus.AWAITING_PAYMENT.value,
            # If sale freshly validated, generate tickets
            'tickets_generated': (status
                                  and self.status not in OrderStatus.VALIDATED_LIST.value
                                  and status.value in OrderStatus.VALIDATED_LIST.value),
        }

        # Update order status
        if resp['updated']:
            self.status = status.value
            self.save()

        # Generate tickets if needed
        if resp['tickets_generated']:
            self.generate_orderlineitems_and_fields()

        resp['status']  = self.get_status_display()
        resp['message'] = OrderStatus.MESSAGES.value[self.status]
        return resp

    @transaction.atomic
    def generate_orderlineitems_and_fields(self) -> int:
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
        link_order = f"http://assos.utc.fr/woolly/commandes/{self.pk}"
        order_list = "".join(f" - {ol.quantity} {ol.item.name}\n" for ol in self.orderlines.all())
        message = (
            "Bonjour {self.owner.get_full_name()},\n\n"
            f"Votre commande n°{self.pk} vient d'être confirmée.\n"
            f"Vous avez commandé:\n{order_list}"
            f"Vous pouvez télécharger vos billets ici : {link_order}\n\n"
            "Merci d'avoir utilisé Woolly"
        )

        email = EmailMessage(
            subject="Woolly - Confirmation de commande",
            body=message,
            from_email="woolly@assos.utc.fr",
            to=[self.owner.email],
            reply_to=["woolly@assos.utc.fr"],
        )
        return email.send()

    def __str__(self) -> str:
        return f"N°{self.id} [{self.get_status_display()}] by {self.owner}"

    class Meta:
        ordering = ('-id',)


class OrderLine(models.Model):
    """
    Links an Order to an Item with a quantity
    """
    item     = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orderlines', editable=False)
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderlines', editable=False)
    quantity = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f"{self.id} - {self.quantity} x {self.item.name} (Order {self.order})"

    class Meta:
        ordering = ('id',)


class OrderLineItem(models.Model):
    """
    Represents a single OrderLine.item with a unique uuid for ticketing
    May have specifications with related OrderLineFields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orderline = models.ForeignKey(OrderLine, on_delete=models.CASCADE, related_name="orderlineitems")

    def __str__(self) -> str:
        return f"{self.id} - {self.orderline}"

    class Meta:
        ordering = ('id',)


# --------------------------------------------
#   Fields
# --------------------------------------------

class Field(models.Model):
    """
    Defines an Item's specification
    """
    id      = models.CharField(max_length=32, primary_key=True)
    name    = models.CharField(max_length=NAME_FIELD_MAXLEN)  # TODO label
    type    = models.CharField(max_length=32)
    default = models.CharField(max_length=254, blank=True, null=True)
    items   = models.ManyToManyField(Item,
                                     through='ItemField',
                                     through_fields=('field', 'item'))

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"

    class Meta:
        ordering = ('id',)


class ItemField(models.Model):
    """
    Links an Item to a Field with additionnal options
    """
    field = models.ForeignKey(Field,
                              on_delete=models.CASCADE,
                              related_name='itemfields',
                              editable=False)
    item  = models.ForeignKey(Item,
                              on_delete=models.CASCADE,
                              related_name='itemfields',
                              editable=False)
    editable = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.item} - {self.field}"

    class Meta:
        ordering = ('id',)


class OrderLineField(models.Model):
    """
    Specifies the Field value taken by the OrderLine Item
    """
    orderlineitem = models.ForeignKey(OrderLineItem,
                                      on_delete=models.CASCADE,
                                      related_name='orderlinefields')
    field = models.ForeignKey(Field,
                              on_delete=models.CASCADE,
                              related_name='orderlinefields')
    value = models.CharField(max_length=512, blank=True, null=True, editable='is_editable')

    def is_editable(self) -> bool:
        itemfield = ItemField.objects.get(
            field__pk=self.field.pk,
            item__pk=self.orderlineitem.orderline.item.pk
        )
        return itemfield.editable

    def __str__(self) -> str:
        return f"{self.orderlineitem.id} - {self.field.name} = {self.value}"

    class Meta:
        ordering = ('id',)
