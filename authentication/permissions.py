from rest_framework import permissions
from .models import User, UserType


class IsUser(permissions.BasePermission):
	"""Custom permission class to allow only order owners to edit them."""
	# def has_permission(self, request, view):
		# return False
	def has_object_permission(self, request, view, obj):
		"""Return True if permission is granted to the order owner."""
		if isinstance(obj, User):
			return obj == request.user

		return obj.user == request.user
