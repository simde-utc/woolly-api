from django.db import models


class ItemGroup(models.Model):
	name = models.CharField(max_length=200)