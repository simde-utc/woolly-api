from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from woolly_api.settings import TEST_MODE
from core.models import APIModel
from authentication.exceptions import UserTypeValidationError

NAME_FIELD_MAXLEN = 100


class UserType(models.Model):
	id = models.CharField(max_length=25, primary_key=True)
	name = models.CharField(max_length=50)
	validation = models.CharField(max_length=255)

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
			print(f"Created {', '.join(created)}.")
		else:
			print("No new usertype to create.")

	def check_user(self, user: 'User') -> bool:
		"""
		Check if the user has the current type
		"""
		if not isinstance(user, User):
			raise ValueError("Provided user must be an instance of authentication.User")
		if not TEST_MODE and not getattr(user, 'fetched_data', None):
			raise ValueError("User full data must be fetched first")
		try:
			return eval(self.validation, {}, { 'user': user })
		except Exception as error:
			raise UserTypeValidationError.from_usertype(self) from error

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "User Type"
		ordering = ('id',)

class User(AbstractBaseUser, APIModel):
	"""
	Woolly User, directly linked to the Portail
	"""
	id = models.UUIDField(primary_key=True, editable=False)
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=NAME_FIELD_MAXLEN)
	last_name  = models.CharField(max_length=NAME_FIELD_MAXLEN)

	# Relations
	types = None
	assos = None

	# Rights
	is_admin = models.BooleanField(default=False)

	# Remove unused AbstractBaseUser.fields
	password = None

	USERNAME_FIELD = 'id'
	EMAIL_FIELD = 'email'  # TODO ???

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

	def get_with_api_data_and_assos(self, oauth_client=None, save: bool=True, try_cache: bool=True):
		# Try to get at least fetched_data from cache
		fetched_data = None
		if try_cache:
			cached = self.get_from_cache({ 'pk': self.pk }, single_result=True, need_full_data=True)
			if cached is not None:
				# Try to get fetched_data and assos from cache
				if cached.assos is not None:
					return cached
				fetched_data = cached.fetched_data

		# If fetched_data cannot be retrieved from cache, fetch it and save it if required
		self.sync_data(fetched_data, oauth_client, save=(fetched_data is None and save))

		# Sync assos
		self.sync_assos(oauth_client=oauth_client)

		return self

	# Sync methods

	def sync_data(self, *args, usertypes=None, save: bool=True, **kwargs):
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
			raise ValueError("Must fetch data from API first")
		if usertypes is None:
			usertypes = UserType.objects.all()

		self.types = {
			usertype.id: usertype.check_user(self)
			for usertype in usertypes
		}

	def sync_assos(self, assos: list=None, oauth_client=None):
		# Fetch assos if needed
		if assos is None:
			user_uri = self.get_api_endpoint({ 'me': True, 'with_types': False })
			assos = oauth_client.fetch_resource(f"{user_uri}/assos")

		# Attach asso by id
		# FIXME Set comprehension not working, invalid character in identifier
		# self.assos = { asso['id'] for asso in assos }
		self.assos = set(str(asso['id']) for asso in assos)

	# Control methods

	def is_type(self, usertype: UserType) -> bool:
		"""
		Check if user is of specified type
		"""
		if self.types is None:
			self.sync_types()
		return self.types.get(usertype, False)

	def is_manager_of(self, asso_id: str) -> bool:
		if self.assos is None:
			raise ValueError("Must fetch associations from API first")
		return str(asso_id) in self.assos

	@property
	def is_staff(self) -> bool:
		"""Grant access to django admin site"""
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return True		# TODO ???

	def has_module_perms(self, app_label):
		return True		# TODO ???
