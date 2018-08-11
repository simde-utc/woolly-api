from rest_framework import permissions
from .models import *

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

# For UserType
class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user and request.user.is_admin
