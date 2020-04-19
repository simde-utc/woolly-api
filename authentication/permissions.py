from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsUserOrAdmin(permissions.BasePermission):
	"""
	Custom permission class to allow only order owners and admin to edit them.
	"""
	def has_permission(self, request, view):
		if view.action is None:
			raise MethodNotAllowed(request.method)

		user = request.user
		# Need to be connected
		if not user.is_authenticated:
			return False

		# Normal users can only retrieve and update themselves
		if view.action in ('list', 'create', 'destroy'):
			return user.is_admin

		return True

	def has_object_permission(self, request, view, obj):
		return request.user.is_admin or obj == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_authenticated and request.user.is_admin
