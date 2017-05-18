from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from core.models.woollyUserManager import WoollyUserManager
from core.models.woollyUserType import WoollyUserType


class WoollyUser(AbstractBaseUser):
	login = models.CharField(max_length=253, unique=True, blank=False)
	type = models.ForeignKey(WoollyUserType, on_delete=None, null=False,default=5)
	# required by Django.admin
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = WoollyUserManager()

	USERNAME_FIELD = 'login'
	EMAIL_FIELD = 'login'
	REQUIRED_FIELDS = []

	# required by Django 1.11 for the User class
	def get_full_name(self):
		return (self.login)

	def get_short_name(self):
		return (self.login)

	# required by Django.admin
	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin

	def save(self, *args, **kwargs):
		if not self.pk:
			self.type_id = 5
		if not self.pk and self.has_usable_password() is False:
			self.set_password(self.password)
		super(WoollyUser, self).save(*args, **kwargs)

	# check set_unusable_password() for authentication against
	# external source
