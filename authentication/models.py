from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.models import ApiModel
import datetime


class UserType(models.Model):
	id = models.CharField(max_length=25, primary_key=True)
	name = models.CharField(max_length=50)
	validation = models.CharField(max_length=250)

	@staticmethod
	def init_defaults():
		"""
		Initialize the different default UserTypes in DB
		"""
		DEFAULT_USER_TYPES = [
			{
				'id': 'cotisant_bde',
				'name': 'Cotisant BDE',
				'validation': 'user.fetched_data["types"]["contributorBde"]',
			},
			{
				'id': 'utc',
				'name': 'UTC',
				'validation': 'user.fetched_data["types"]["cas"]',
			},
			{
				'id': 'tremplin',
				'name': 'Tremplin UTC',
				'validation': 'user',
			},
			{
				'id': 'exterieur',
				'name': 'Extérieur',
				'validation': 'True',
			},
		]
		created = []
		for type_data in DEFAULT_USER_TYPES:
			pk = type_data.pop('id')
			if UserType.objects.get_or_create(defaults=type_data, pk=pk)[1]:
				created.append(pk)

		if created:
			print(f"Created {', '.join(created)}")

	def check_user(self, user: 'User') -> bool:
		"""
		Check if the user has the current type
		"""
		if not isinstance(user, User):
			raise ValueError("Provided user must be an instance of authentication.User")
		return eval(self.validation)

	def __str__(self):
		return self.name

	class Meta:
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
	types = None

	# Rights
	is_admin = models.BooleanField(default=False)

	# Remove unused AbstractBaseUser.fields
	password = None

	USERNAME_FIELD = 'id'
	EMAIL_FIELD = 'email' # TODO ???

	def __str__(self):
		return self.get_full_name()

	def get_full_name(self):
		return f"{self.first_name} {self.last_name}"

	def get_short_name(self):
		return self.first_name

	# OAuth API methods

	def get_api_endpoint(cls, **params) -> str:
		# if params.get('me', False):
		# 	return 
		# return (f"users/{user_id}" if user_id else "user") + "/?types=*"

		pass

	@staticmethod
	def patch_fetched_data(data: dict) -> dict:
		# TODO Checks
		data['first_name'] = data.pop('firstname')
		data['last_name'] = data.pop('lastname')
		data['is_admin'] = data['types']['is_admin']
		return data

	def sync_data(self, *args, usertypes: 'UserTypes'=None, **kwargs):
		"""
		Sync data and also types
		"""
		result = super().sync_data(*args, **kwargs)
		self.sync_types(usertypes)
		return result

	def sync_types(self, usertypes: 'UserType'=None):
		if not self.fetched_data:
			raise ValueError('Must fetch data from API first')
		if usertypes is None:
			usertypes = UserType.objects.all()

		self.types = {
			utype.id: utype.check_user(self)
			for utype in usertypes
		}

	# required by Django.admin TODO
	
	@property
	def is_staff(self):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True		# ???

	def has_module_perms(self, app_label):
		return True		# ???
