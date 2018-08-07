from rest_framework import permissions
from .models import User, UserType

class IsOwner(permissions.BasePermission):
	"""
	Custom permission class to allow only order owners to edit them.
	"""
	def has_permission(self, request, view):
		return request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if isinstance(obj, User):
			return obj == request.user
		return obj.owner == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
	"""
	Custom permission class to allow only order owners and admin to edit them.
	"""
	def has_permission(self, request, view):
		return request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if request.user.is_admin:
			return True

		if isinstance(obj, User):
			print(obj == request.user)
			return obj == request.user
		return obj.owner == request.user
