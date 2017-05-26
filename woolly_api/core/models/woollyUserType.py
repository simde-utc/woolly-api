from django.db import models


class WoollyUserType(models.Model):
	COTISANT = 'cotisant'
	NON_COTISANT = 'non-cotisant'
	TREMPLIN = 'tremplin'
	EXTERIEUR = 'exterieur'
	name = models.CharField(max_length=50, unique=True)

	@staticmethod
	def init_values():
		"""
		initialize the different possible WoollyUserType in DB
		"""
		values = [WoollyUserType.COTISANT, WoollyUserType.NON_COTISANT, WoollyUserType.TREMPLIN, WoollyUserType.EXTERIEUR]
		for value in values:
			n = WoollyUserType(name=value)
			n.save()

