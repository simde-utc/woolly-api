from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import gettext as _
from django.forms import ValidationError
from rest_framework.authentication import BaseAuthentication

UserModel = get_user_model()


class APIAuthentication(BaseAuthentication):
	"""
	Authenticate User frow request, used in the API
	"""

	def authenticate(self, request):
		"""
		Return the user from the JWT sent in the request
		"""
		user_id = request.session.get('user_id')
		if user_id:
			request.user = UserModel.objects.get(pk=user_id)
			return (request.user, None)
		else:
			return None


class AdminSiteBackend(ModelBackend):
	"""
	Authenticate User from email - password, used in the admin site
	"""

	def authenticate(self, request, username=None, password=None):
		# Try to fetch user
		try:
			user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
		except UserModel.DoesNotExist:
			return None

		# Check password
		if not user.check_password(password):
			return None

		# Check if admin
		if not user.is_admin:
			raise ValidationError(
				_("This account is not allowed."),
				code='not_allowed',
			)

		return user

	def get_user(self, user_id):
		try:
			return UserModel.objects.get(id=user_id)
		except UserModel.DoesNotExist:
			return None
