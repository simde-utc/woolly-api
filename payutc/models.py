from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


import datetime

"""
class UserType(models.Model):
    COTISANT = 'cotisant'
    NON_COTISANT = 'non-cotisant'
    TREMPLIN = 'tremplin'
    EXTERIEUR = 'exterieur'
    name = models.CharField(max_length=50, unique=True)

    @staticmethod
    def init_values():
        "" "
        initialize the different possible WoollyUserType in DB
        "" "
        values = [WoollyUserType.COTISANT, WoollyUserType.NON_COTISANT,
                  WoollyUserType.TREMPLIN, WoollyUserType.EXTERIEUR]
        for value in values:
            n = WoollyUserType(name=value)
            n.save()

    class JSONAPIMeta:
        resource_name = "woollyusertypes"


class WoollyUserManager(BaseUserManager):
    # required by Django

    def create_user(self, login, password=None, **other_fields):
        if not login:
            raise ValueError('The given login must be set')
        user = self.model(login=login,
                          **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # required by Django
    def create_superuser(self, login, password, **other_fields):
        user = self.create_user(login,
                                password=password,
                                **other_fields
                                )
        user.is_admin = True
        user.save(using=self._db)
        return user


class WoollyUser(AbstractBaseUser):
    login = models.CharField(max_length=253, unique=True, blank=False)

    woollyusertype = models.ForeignKey(
        WoollyUserType, on_delete=None, null=False, default=4, related_name='users')

    associations = models.ManyToManyField('sales.Association', through='sales.AssociationMember')
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

    class JSONAPIMeta:
        resource_name = "woollyusers"

    # check set_unusable_password() for authentication against
    # external source
"""