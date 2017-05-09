from django.db import models
from core.models.paymentMethod import PaymentMethod
from core.models.association import Association

class Sale(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	creation_date = models.DateField(auto_now_add=True)
	begin_date = models.DateField()
	end_date = models.DateField()
	max_payment_date = models.DateField()
	max_article_quantity = models.IntegerField()
	payment_methods = models.ManyToManyField(PaymentMethod)
	association = models.ForeignKey(Association, on_delete=None)