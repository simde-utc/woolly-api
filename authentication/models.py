from django.contrib.auth.models import AbstractBaseUser
from django.db import models
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

class User(AbstractBaseUser):
	# Properties
	id = models.UUIDField(primary_key=True, editable=False)
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	# birthdate = models.DateField(default=datetime.date.today)

	# Relations
	usertype = models.ForeignKey(UserType, on_delete=None, null=False, default=4, related_name='users')

	# Rights
	is_admin = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	EMAIL_FIELD = 'email'

	# Display
	def __str__(self):
		return self.email

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

	def get_short_name(self):
		return self.first_name

	# required by Django.admin
	
	@property
	def is_active(self):
		return True

	@property
	def is_staff(self):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True		# ???

	def has_module_perms(self, app_label):
		return True		# ???

	"""
	def save(self, *args, **kwargs):
		if not self.login:
			self.login = None
		# if not self.pk and self.has_usable_password() is False:
			# self.set_password(self.password)
		super(User, self).save(*args, **kwargs)
	"""

	class Meta:
		ordering = ('id',)
