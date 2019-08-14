from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.models import ApiModel
import datetime


class UserType(models.Model):
	name = models.CharField(max_length=50, unique=True)
	# description = models.CharField(max_length=180, unique=True)
	# item = models.ManyToManyField('sales.Item')

	# TODO : revoir ça ?
	COTISANT 	 = 'Cotisant BDE'
	NON_COTISANT = 'UTC Non Cotisant'
	TREMPLIN 	 = 'Tremplin UTC'
	EXTERIEUR 	 = 'Extérieur'

	@staticmethod
	def init_values():
		"""Initialize the different default UserTypes in DB"""
		types = (UserType.COTISANT, UserType.NON_COTISANT, UserType.TREMPLIN, UserType.EXTERIEUR)
		for value in types:
			UserType(name=value).save()

	def __str__(self):
		return self.name

	class Meta:
		ordering = ('id',)
		verbose_name = "User Type"

class User(AbstractBaseUser, ApiModel):
	"""
	Woolly User, directly linked to the Portail
	"""

	id = models.UUIDField(primary_key=True, editable=False)
	email = models.EmailField(unique=True) # TODO
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	# birthdate = models.DateField(default=datetime.date.today)

	# Relations
	usertype = models.ForeignKey(UserType, on_delete=None, null=False, default=4, related_name='users')

	# Rights
	# TODO
	is_admin = models.BooleanField(default=False)


	# Remove unused AbstractBaseUser.fields
	password = None

	USERNAME_FIELD = 'id'
	EMAIL_FIELD = 'email' # TODO ???

	def __str__(self):
		return self.get_full_name()

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

	def get_short_name(self):
		return self.first_name

	# required by Django.admin TODO
	
	@property
	def is_staff(self):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True		# ???

	def has_module_perms(self, app_label):
		return True		# ???

	# def save(self, *args, **kwargs):
		# TODO type
