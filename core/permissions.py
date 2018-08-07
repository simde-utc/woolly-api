from rest_framework import permissions


class CustomPermission(permissions.BasePermission):
	require_authentication = False
	allow_admin = False
	allow_read_only = False

	permission_functions = []
	object_permission_functions = []
	check_with_or = True

	def _check_functions(function_list):
		permission_gen = (f(request, view) for f in function_list)
		return any(permission_gen) if self.check_with_or else all(permission_gen)

	def _is_not_authenticated(self, request, view):
		return not request.user.is_authenticated

	def has_permission(self, request, view):
		# Is Authenticated option
		if self.require_authentication and self._is_not_authenticated:
			return False

		# Read Only option
		if self.allow_read_only and request.method in permissions.SAFE_METHODS:
			return True

		# Check all permission_functions
		if self.permission_functions:
			return self._check_functions(self.permission_functions)

		return True

	def has_object_permission(self, request, view, obj):
		# Allow admin option
		if self.allow_admin and request.user.is_admin:
			return True

		# Check all permission_functions
		if self.object_permission_functions:
			return self._check_functions(self.object_permission_functions)

		return True



class IsAdmin(CustomPermission):
	"""Only Woolly admins have the permission"""
	def has_permission(self, request, view):
		return request.user.is_authenticated and request.user.is_admin

class IsAdminOrReadOnly(permissions.BasePermission):
	"""Only Woolly admins have the permission to modify, anyone can read"""
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_authenticated and request.user.is_admin

class IsAdminOrAuthenticatedReadOnly(permissions.BasePermission):
	"""Only Woolly admins have the permission to modify, authenticated users can read"""
	def has_permission(self, request, view):
		if not request.user.is_authenticated:
			return False
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_admin
