from rest_framework import permissions
from core.permissions import CustomPermission
from .models import *



def object_check_manager(request, view, obj):
	user = request.user
	# TODO
	return user.is_authenticated and user.is_admin

# Used for Association, Sale
class IsManagerOrReadOnly(CustomPermission):
	allow_read_only = True
	object_permission_functions = (object_check_manager,)

# Used for AssociationMember
class IsManager(CustomPermission):
	require_authentication = True
	allow_admin = True
	object_permission_functions = (object_check_manager,)


def check_order_ownership(request, view, obj):
	if isinstance(obj, Order):
		return obj.owner == request.user
	if isinstance(obj, OrderLine):
		return obj.order.owner == request.user
	if isinstance(obj, OrderLineItem):
		return obj.orderline.order.owner == request.user
	if isinstance(obj, OrderLineField):
		return obj.orderitem.orderline.order.owner == request.user
	return False

# Used for Order, OrderLine, OrderLineItem, OrderLineField
class IsOrderOwnerOrAdmin(CustomPermission):
	require_authentication = True
	allow_creation = True
	allow_admin = True
	object_permission_functions = (check_order_ownership,)

