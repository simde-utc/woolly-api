from core.exceptions import InvalidRequest
from core.permissions import CustomPermission
from authentication.oauth import OAuthAPI
from .models import (
	Association, Sale, Item, ItemGroup,
	Order, OrderLine, OrderLineItem, OrderLineField
)


def get_url_param(request, view, name: str):
	param_request = request.data.get(name)
	if param_request:
		return param_request
	else:
		raise InvalidRequest(f"Could not retrieve parameter '{name}' from request")

	# TODO Needed ?
	param_kwargs = view.kwargs.get(f"{name}_pk")

	# Need one or the other or both equal
	if param_request:
		if param_kwargs:
			if param_request != param_kwargs:
				raise InvalidRequest(f"Got different parameter values for '{name}' from request")
			return param_request
	elif param_kwargs:
		return param_kwargs

	raise InvalidRequest(f"Could not retrieve parameter '{name}' from request")


def check_manager(request, view) -> bool:

	Model = view.queryset.model
	if Model not in {Association, Sale, Item, ItemGroup}:
		raise NotImplementedError(f"Object {Model} is not managed")

	if not request.user.is_authenticated:
		return False

	# Get the related association
	asso_id = sale_id = None
	if Model == Association:
		if view.action in {'create', 'delete'}:
			return False
		asso_id = view.kwargs.get('pk')
	elif Model == Sale:
		if 'pk' not in view.kwargs:
			asso_id = get_url_param(request, view, 'association')
		else:
			sale_id = view.kwargs.get('pk')
	elif Model in { Item, ItemGroup }:
		if 'pk' not in view.kwargs:
			sale_id = get_url_param(request, view, 'sale')
		else:
			try:
				sale_id = Model.objects.get(pk=view.kwargs.get('pk')).sale_id
			except Model.DoesNotExist:
				raise InvalidRequest(f"Could not retrieve related {Model.__name__}")

	if sale_id:
		try:
			sale = Sale.objects.get(pk=sale_id)
			asso_id = sale.association_id
		except Sale.DoesNotExist:
			raise InvalidRequest("Could not retrieve related Sale")

	if not Association.objects.filter(pk=asso_id).exists():
		raise InvalidRequest(f"Could not retrieve association '{asso_id}'")

	# Get user's associations and check if is manager
	oauth_client = OAuthAPI(session=request.session)
	user = request.user.get_with_api_data_and_assos(oauth_client)
	return user.is_manager_of(asso_id)


# Used for Association, Sale, ItemGroup, Item, ItemField
class IsManagerOrReadOnly(CustomPermission):
	allow_read_only = True
	permission_functions = (check_manager,)
	default_obj = True  # No additional check for object


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
