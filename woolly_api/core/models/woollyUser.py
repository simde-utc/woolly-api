from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from core.models.woollyUserManager import WoollyUserManager
from core.models.woollyUserType import WoollyUserType

import datetime


class WoollyUser(AbstractBaseUser):
	login = models.CharField(max_length=253, unique=True, blank=False)

	type = models.ForeignKey(WoollyUserType, on_delete=None, null=False, default=4)

	last_name = models.CharField(max_length=100, blank=True)
	first_name = models.CharField(max_length=100, blank=True)
	email = models.EmailField(blank=True)
	birthdate = models.DateField(default=datetime.date.today)

	# required by Django.admin
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = WoollyUserManager()

	USERNAME_FIELD = 'login'
	EMAIL_FIELD = 'email'
	REQUIRED_FIELDS = []

	# required by Django 1.11 for the User class
	def get_full_name(self):
		ret = self.first_name + ' ' + self.last_name
		return ret if ret else self.login

	def get_short_name(self):
		ret = self.first_name
		return ret if ret else self.login

	# required by Django.admin
	def has_perm(self, perm, obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

	@property
	def is_staff(self):
		return self.is_admin

	def save(self, *args, **kwargs):
		if not self.pk and self.has_usable_password() is False:
			self.set_password(self.password)
		super(WoollyUser, self).save(*args, **kwargs)

	# check set_unusable_password() for authentication against
	# external source
