from django.db import models


class Association(models.Model):
	name = models.CharField(max_length=200)
	bank_account = models.CharField(max_length=30)
