from rest_framework.permissions import BasePermission
from .models import Order

class IsOwner(BasePermission):
    """Custom permission class to allow only order owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the order owner."""
        if isinstance(obj, Order):
            return obj.user == request.user
        return obj.user == request.user
