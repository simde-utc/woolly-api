from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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
		"""
		initialize the different default UserTypes in DB
		"""
		types = (UserType.COTISANT, UserType.NON_COTISANT, UserType.TREMPLIN, UserType.EXTERIEUR)
		for value in types:
			UserType(name=value).save()

	class JSONAPIMeta:
		resource_name = "usertypes"


class UserManager(BaseUserManager):
	def create_user(self, email=None, password=None, **other_fields):
		if not email:
			raise ValueError('The given email must be set')
		user = self.model(email=email, **other_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, **other_fields):
		# TODO Create a hash password and set it by email
		password = "hash"

		user = self.create_user(email, password=password, **other_fields)
		user.is_admin = True
		user.save(using=self._db)
		return user


class User(AbstractBaseUser):
	# Properties
	email = models.EmailField(unique=True)
	login = models.CharField(max_length=253, unique=True, blank=True, null=True)  # TODO : virer	
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	birthdate = models.DateField(default=datetime.date.today)

	# Relations
	usertype = models.ForeignKey(UserType, on_delete=None, null=False, default=4, related_name='users')
	# associations = models.ManyToManyField('sales.Association', through='sales.AssociationMember')

	# Rights
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	@property
	def is_staff(self):
		return self.is_admin

	objects = UserManager()

	USERNAME_FIELD = 'email'
	EMAIL_FIELD = 'email'

	# Display
	def __str__(self):
		return '%s %s %s' % (self.email, self.first_name, self.usertype.name)

	

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

	def get_short_name(self):
		return self.first_name

	"""
	# required by Django.admin
	def has_perm(self, perm, obj=None):
		return True		# ???

	def has_module_perms(self, app_label):
		return True		# ???


	def save(self, *args, **kwargs):
		if not self.login:
			self.login = None
		# if not self.pk and self.has_usable_password() is False:
			# self.set_password(self.password)
		super(User, self).save(*args, **kwargs)
	"""

	class Meta:
		# default_manager_name = UserManager
		pass

	class JSONAPIMeta:
		resource_name = "users"

	# check set_unusable_password() for authentication against external source
