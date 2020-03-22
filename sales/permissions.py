from core.permissions import CustomPermission
from authentication.oauth import OAuthAPI
from .models import (
	Association, Sale, Item, ItemGroup,
	Order, OrderLine, OrderLineItem, OrderLineField
)


def check_manager(request, view) -> bool:

	model = view.queryset.model
	if model not in (Sale, Item, ItemGroup):
		raise NotImplementedError(f"Object {view.queryset.model} is not managed")

	if not request.user.is_authenticated:
		return False

	# Get the related association
	asso_id = None
	if model == Sale:
		asso_id = request.data.get('association')
		# TODO Deal with /assos/azd/sale from request.path
	elif model == Item:
		pass  # TODO
	elif model == ItemGroup:
		pass  # TODO

	if asso_id is None:
		# TODO Return 400 BAD REQUEST
		raise ValueError("Could not retrieve asso id")

	oauth_client = OAuthAPI(session=request.session)

	try:
		asso = Association.objects.get(pk=asso_id)
	except Association.DoesNotExists:
		asso = Association.objects.get_with_api_data(oauth_client, pk=asso_id)

	# Get user's associations and check if is manager
	user = request.user.get_with_api_data_and_assos(oauth_client)
	return user.is_manager_of(asso)

def object_check_manager(request, view, obj) -> bool:
	return True  # TODO Needed ??
	# assert view.queryset.model in (Sale, Item, ItemGroup)
	# # TODO
	# return user.is_authenticated and user.is_admin

# Used for Association, Sale, ItemGroup, Item, ItemField
class IsManagerOrReadOnly(CustomPermission):
	allow_read_only = True
	permission_functions = (check_manager,)
	# object_permission_functions = (object_check_manager,)


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
