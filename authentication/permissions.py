from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsUserOrAdmin(permissions.BasePermission):
    """
    Allow only access to current user to the admin and the user
    """
    def has_permission(self, request, view) -> bool:
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

    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_admin or obj == request.user
