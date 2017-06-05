from django.db import models
from authentication.models import WoollyUserType


class Association(models.Model):
    name = models.CharField(max_length=200)
    bank_account = models.CharField(max_length=30)

    class JSONAPIMeta:
        resource_name = "associations"


class PaymentMethod(models.Model):
    """Define the payment options"""
    name = models.CharField(max_length=200)
    api_url = models.CharField(max_length=500)

    class JSONAPIMeta:
        resource_name = "paymentmethods"


class Sale(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    creation_date = models.DateField(auto_now_add=True)
    begin_date = models.DateField()
    end_date = models.DateField()
    max_payment_date = models.DateField()
    max_item_quantity = models.IntegerField()
    # payment_methods = models.ManyToManyField(PaymentMethod)
    association = models.ForeignKey(
        Association, on_delete=None, related_name='sales', blank=True)

    class JSONAPIMeta:
        resource_name = "sales"


# Should be in a Authentication app

# class WoollyUserType(models.Model):
#    name = models.CharField(max_length=50, unique=True)

#    class JSONAPIMeta:
#        resource_name = "woollyusertypes"
###

# class ItemGroup(models.Model):
# name = models.CharField(max_length=200)


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    remaining_quantity = models.IntegerField()
    initial_quantity = models.IntegerField()
    # group = models.ForeignKey(ItemGroup, on_delete=None, related_name='items'
    # ,blank=True)
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE, related_name='items')

    class JSONAPIMeta:
        resource_name = "items"


class ItemSpecifications(models.Model):
    woolly_user_type = models.ForeignKey(
        WoollyUserType, on_delete=models.CASCADE, related_name='specs')
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='specifications')
    quantity = models.IntegerField()
    price = models.FloatField()

    class JSONAPIMeta:
        resource_name = "itemspecifications"


class Order(models.Model):
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)
    date = models.DateField()

    class JSONAPIMeta:
        resource_name = "orders"


class OrderLine(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField()

    class JSONAPIMeta:
        resource_name = "orderlines"
