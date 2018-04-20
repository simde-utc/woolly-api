from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
import datetime

"""
class OAuth2Token(models.Model):
	name = models.CharField(max_length=40)
	token_type = models.CharField(max_length=20)
	access_token = models.CharField(max_length=200)
	refresh_token = models.CharField(max_length=200)
	# oauth 2 expires time
	expires_at = models.DateTimeField()
	# ...

	def to_token(self):
		return dict(
			access_token=self.access_token,
			token_type=self.token_type,
			refresh_token=self.refresh_token,
			expires_at=self.expires_at,
		)
"""

class WoollyUserType(models.Model):
	name = models.CharField(max_length=50, unique=True)
	# description = models.CharField(max_length=180, unique=True)

	# TODO : revoir ça ?
	COTISANT = 'cotisant'
	NON_COTISANT = 'non-cotisant'
	TREMPLIN = 'tremplin'
	EXTERIEUR = 'extérieur'

	@staticmethod
	def init_values():
		"""
		initialize the different default WoollyUserTypes in DB
		"""
		types = [WoollyUserType.COTISANT, WoollyUserType.NON_COTISANT, WoollyUserType.TREMPLIN, WoollyUserType.EXTERIEUR]
		for value in types:
			WoollyUserType(name=value).save()

	class JSONAPIMeta:
		resource_name = "woollyusertypes"


"""
class WoollyUserManager(BaseUserManager):
	# required by Django
	def create_user(self, login='', password=None, **other_fields):
		if not login:
			raise ValueError('The given login must be set')
		user = self.model(login=login, **other_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	# required by Django
	def create_superuser(self, login, password, **other_fields):
		user = self.create_user(login, password=password, **other_fields)
		user.is_admin = True
		user.save(using=self._db)
		return user
"""

class WoollyUser(AbstractBaseUser):
	# Properties
	email = models.EmailField(unique=True)
	login = models.CharField(max_length=253, unique=True, blank=True, null=True) 
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	birthdate = models.DateField(default=datetime.date.today)

	# Associations
	woollyusertype = models.ForeignKey(WoollyUserType, on_delete=None, null=False, default=4, related_name='users')
	associations = models.ManyToManyField('sales.Association', through='sales.AssociationMember')

	# required by Django.is_admin => A virer pour remplacer par les droits
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	# objects = WoollyUserManager()

	# Cas
	USERNAME_FIELD = 'id'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = []

	"""
	# required by Django 1.11 for the User class
	def get_full_name(self):
		ret = self.first_name + ' ' + self.last_name
		return ret if ret else self.login

	def get_short_name(self):
		ret = self.first_name
		return ret if ret else self.login

	# required by Django.admin
	def has_perm(self, perm, obj=None):
		return True		# ???

	def has_module_perms(self, app_label):
		return True		# ???

	@property
	def is_staff(self):
		return self.is_admin

	def save(self, *args, **kwargs):
		if not self.login:
			self.login = None
		# if not self.pk and self.has_usable_password() is False:
			# self.set_password(self.password)
		super(WoollyUser, self).save(*args, **kwargs)
	"""

	class Meta:
		# default_manager_name = WoollyUserManager
		pass

	class JSONAPIMeta:
		resource_name = "woollyusers"

	# check set_unusable_password() for authentication against external source
