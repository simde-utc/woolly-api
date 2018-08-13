from rest_framework import permissions
from core.permissions import CustomPermission
from .models import *



def object_check_manager(request, view, obj):
	user = request.user
	# TODO
	return user.is_authenticated and user.is_admin

# Used for Association, Sale, ItemGroup, Item, ItemField
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
		return obj.orderlineitem.orderline.order.owner == request.user
	return False

# Used for Order, OrderLine
class IsOrderOwnerOrAdmin(CustomPermission):
	require_authentication = True
	pass_for_obj = True
	allow_admin = True
	allow_create = True
	object_permission_functions = (check_order_ownership,)


def allow_only_retrieve_for_non_admin(request, view):
	return view.action == 'retrieve' or request.user.is_admin

# Used for OrderLineItem
class IsOrderOwnerReadOnlyOrAdmin(CustomPermission):
	require_authentication = True
	permission_functions = (allow_only_retrieve_for_non_admin,)
	object_permission_functions = (check_order_ownership,)

def no_delete(request, view, obj):
	return not view.action == 'destroy'

# Used for OrderLineField
class IsOrderOwnerReadUpdateOrAdmin(CustomPermission):
	require_authentication = True
	pass_for_obj = True
	allow_admin = True
	object_permission_functions = (check_order_ownership, no_delete)
	check_with_or = False
