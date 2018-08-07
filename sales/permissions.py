from rest_framework import permissions
from core.permissions import CustomPermission
from .models import *


def check_ownership(request, view, obj):
	if isinstance(obj, Order):
		return obj.owner == request.user
	if isinstance(obj, OrderLine):
		return obj.order.owner == request.user
	if isinstance(obj, OrderLineItem):
		return obj.orderline.order.owner == request.user
	if isinstance(obj, OrderLineField):
		return obj.orderitem.orderline.order.owner == request.user

class IsOwner(CustomPermission):
	require_authentication = True
	object_permission_functions = (check_ownership,)

class IsOwnerOrAdmin(IsOwner):
	allow_admin = True

class IsOwnerOrReadOnly(IsOwner):
	allow_read_only = True


# TODO
def check_manager(request, view, obj):
	return request.user.is_admin


class IsManager(CustomPermission):
	require_authentication = True
	object_permission_functions = (check_manager,)

class IsManagerOrReadOnly(CustomPermission):
	allow_read_only = True

