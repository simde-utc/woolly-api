from rest_framework import permissions
from .models import User, UserType

class IsUserOrAdmin(permissions.BasePermission):
	"""
	Custom permission class to allow only order owners and admin to edit them.
	"""
	def has_permission(self, request, view):
		user = request.user
		# Need to be connected
		if not user.is_authenticated:
			return False

		# IMPORTANT Normal users can only retrieve and update themselves
		if view.action in ('list', 'create', 'destroy'):
			return user.is_admin

		return True

	def has_object_permission(self, request, view, obj):
		user = request.user
		return user.is_admin or obj == user
