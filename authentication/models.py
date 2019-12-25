from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from core.models import ApiModel
import datetime


class UserTypeValidationError(Exception):

	def __init__(self, usertype: 'UserType'):
		self.message = f"Cannot validate usertype {usertype}\n(validation: {usertype.validation}"
		super().__init__(self.message)


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
		try:
			return eval(self.validation, {}, { 'user': user })
		except Exception as error:
			raise UserTypeValidationError(self) from error

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "User Type"
		ordering = ('id',)

class User(AbstractBaseUser, ApiModel):
	"""
	Woolly User, directly linked to the Portail
	"""
	id = models.UUIDField(primary_key=True, editable=False)
	email = models.EmailField(unique=True) # TODO
	first_name = models.CharField(max_length=100)
	last_name  = models.CharField(max_length=100)

	# Relations
	types = None

	# Rights
	is_admin = models.BooleanField(default=False)

	# Remove unused AbstractBaseUser.fields
	password = None

	USERNAME_FIELD = 'id'
	EMAIL_FIELD = 'email' # TODO ???

	def __str__(self) -> str:
		return self.get_full_name()

	def get_full_name(self) -> str:
		return f"{self.first_name} {self.last_name}"

	def get_short_name(self) -> str:
		return self.first_name

	# OAuth API methods

	@classmethod
	def get_api_endpoint(cls, params: dict) -> str:
		if params.get('me', False):
			url = 'user'
		elif 'pk' in params:
			url = f"users{cls.pk_to_url(params['pk'])}"
		else:
			url = 'users'
		if params.get('with_types', True):
			url += '/?types=*'
		return url

	@staticmethod
	def patch_fetched_data(data: dict) -> dict:
		# TODO Checks
		data['first_name'] = data.pop('firstname')
		data['last_name'] = data.pop('lastname')
		data['is_admin'] = data['types']['admin']
		return data

	def sync_data(self, *args, usertypes: 'UserTypes'=None, save: bool=True, **kwargs):
		"""
		Synchronise data, keep manually-set admin and also types
		"""
		was_admin = self.is_admin
		# Sync data and types
		updated_fields = super().sync_data(*args, save=False, **kwargs)
		self.sync_types(usertypes)

		# Keep admin if set manually
		if was_admin and not self.is_admin:
			self.is_admin = True

		# Save if needed
		if save and updated_fields:
			self.save()

		return updated_fields

	def sync_types(self, usertypes: UserType=None):
		"""
		Synchronise UserTypes to the user
		"""
		if not self.fetched_data:
			raise ValueError('Must fetch data from API first')
		if usertypes is None:
			usertypes = UserType.objects.all()

		self.types = {
			usertype.id: usertype.check_user(self)
			for usertype in usertypes
		}

	def is_type(self, usertype: UserType) -> bool:
		"""
		Check if user is of specified type
		"""
		if self.types is None:
			self.sync_types()
		return self.types.get(usertype, False)

	# required by Django.admin TODO
	
	@property
	def is_staff(self):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True		# ???

	def has_module_perms(self, app_label):
		return True		# ???
