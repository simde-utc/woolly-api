from django.db import models
from core.models.item import Item
from core.models.order import Order


class OrderLine(models.Model):
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	# à étudier
	# price =