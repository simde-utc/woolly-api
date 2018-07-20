from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
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
		if request.user.is_authenticated == False:
			return False
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_admin
