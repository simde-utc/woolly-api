from django.db import models
from core.models.itemGroup import ItemGroup


class Item(models.Model):
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=1000)
	remaining_quantity = models.IntegerField()
	initial_quantity = models.IntegerField()
	item_group = models.ForeignKey(ItemGroup, on_delete=None)
	#specifications = models.ManyToManyField(WoollyUserType, through='ItemSpecifications')
