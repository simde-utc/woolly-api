from django.db import models
from core.models.paymentMethod import PaymentMethod
from core.models.item import Item
from django.contrib.auth import get_user_model

class Order(models.Model):
	quantity = models.IntegerField()
	date = models.DateField(auto_now_add=True)
	items = models.ManyToManyField(Item, through='OrderLine', related_name='items')
	user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

	# to be done, not enough time now
	# status = models.CharField(max_length=1, choices=)

	#the payment method must be authorized by the sale
	#payment_method = models.ForeignKey(PaymentMethod, on_delete=None)
