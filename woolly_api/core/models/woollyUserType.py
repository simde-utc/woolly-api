from django.db import models


class WoollyUserType(models.Model):
	name = models.CharField(max_length=50, unique=True)
