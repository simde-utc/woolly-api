from rest_framework import permissions
from .models import Order


class IsOwner(permissions.BasePermission):
	"""Custom permission class to allow only order owners to edit them."""
	def has_object_permission(self, request, view, obj):
		"""Return True if permission is granted to the order owner."""
		if isinstance(obj, Order):
			return obj.user == request.user
		return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
	"""
	Object-level permission to only allow owners of an object to edit it.
	Assumes the model instance has an `owner` attribute.
	"""
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True

		# Instance must have an attribute named `owner`.
		return obj.owner == request.user

class IsManager(permissions.BasePermission):
	"""Only assos' manager have the permission to modify"""
	def has_permission(self, request, view):
		# TODO
		return request.user.is_authenticated and request.user.is_admin

class IsManagerOrReadOnly(permissions.BasePermission):
	"""Only assos' manager have the permission to modify, anyone can read"""
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		# TODO
		return request.user.is_authenticated and request.user.is_admin

