from django.db import models
from core.models.woollyUserType import WoollyUserType
from core.models.item import Item


class ItemSpecifications(models.Model):
	woolly_user_type = models.ForeignKey(WoollyUserType, on_delete=models.CASCADE)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	price = models.FloatField()