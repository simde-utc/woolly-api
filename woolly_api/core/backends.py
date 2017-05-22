from cas.backends import CASBackend
from cas.backends import _verify
from django.contrib.auth import get_user_model
from django.conf import settings


class UpdatedCASBackend(CASBackend):
	def authenticate(self, ticket, service):
		"""
		Verifies CAS ticket and gets or creates User object
		NB: Use of PT to identify proxy
		"""

		UserModel = get_user_model()
		username = _verify(ticket, service)
		if not username:
			return None

		try:
			user = UserModel._default_manager.get(**{
				UserModel.USERNAME_FIELD: username
			})
			import pdb; pdb.set_trace()
		except UserModel.DoesNotExist:
			# user will have an "unusable" password
			if settings.CAS_AUTO_CREATE_USER:
				user = UserModel.objects.create_user(username, '')
				user.save()
			else:
				user = None
		return user
