from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed

from core.exceptions import InvalidRequest
from core.permissions import CustomPermission
from authentication.oauth import OAuthAPI
from .models import (
    Association, Sale, Item, ItemGroup, ItemField,
    Order, OrderLine, OrderLineItem, OrderLineField
)


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Check that a user is manager of the Association
    related to the target resource

    Used for Association, Sale, ItemGroup, Item, ItemField
    """

    def get_url_param(self, name: str):
        param_request = self.request.data.get(name)
        if param_request:
            return param_request
        else:
            raise InvalidRequest(f"Could not retrieve parameter '{name}' from request")

        # TODO Needed ?
        """
        param_kwargs = self.view.kwargs.get(f"{name}_pk")

        # Need one or the other or both equal
        if param_request:
            if param_kwargs:
                if param_request != param_kwargs:
                    raise InvalidRequest(f"Got different parameter values for '{name}' from request")
                return param_request
        elif param_kwargs:
            return param_kwargs

        raise InvalidRequest(f"Could not retrieve parameter '{name}' from request")
        """

    def get_related_model(self, Model, pk, *related):
        try:
            query = Model.objects
            if related:
                query = query.select_related(*related)
            return query.get(pk=pk)
        except Model.DoesNotExist:
            raise InvalidRequest(f"Could not retrieve related {Model.__name__}")

    def get_related_asso_id(self, request, view) -> str:
        Model = view.queryset.model
        if Model not in { Association, Sale, Item, ItemGroup, ItemField }:
            raise NotImplementedError(f"Model {Model} is not managed")

        if view.action is None:
            raise MethodNotAllowed(request.method)

        hasPk = 'pk' in view.kwargs
        pk = view.kwargs.get('pk')

        if Model == Association:
            if view.action in {'create', 'delete'}:
                return False
            else:
                return view.kwargs.get('pk')

        elif Model == Sale:
            if hasPk:
                return self.get_related_model(Sale, pk).association_id
            else:
                return self.get_url_param('association')

        elif Model in { Item, ItemGroup }:
            if hasPk:
                return self.get_related_model(Model, pk, 'sale').sale.association_id
            else:
                sale_pk = self.get_url_param('sale')
                return self.get_related_model(Sale, sale_pk).association_id

        elif Model == ItemField:
            if hasPk:
                return self.get_related_model(ItemField, pk, 'item__sale').item.sale.association_id
            else:
                item_pk = self.get_url_param('item')
                return self.get_related_model(Item, item_pk, 'sale').sale.association_id

        raise InvalidRequest("Could not retrieve related Association")

    def has_permission(self, request, view) -> bool:
        # Check view's Model
        Model = view.queryset.model
        if Model not in {Association, Sale, Item, ItemGroup, ItemField}:
            raise NotImplementedError(f"Object {Model} is not managed")

        # Allow read only
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False
        if request.user.is_admin:
            return True

        # Get the related association
        asso_id = self.get_related_asso_id(request, view)

        # Check that the association is real
        if not Association.objects.filter(pk=asso_id).exists():
            raise InvalidRequest(f"Could not retrieve association '{asso_id}'")

        # Get user's associations and check if is manager
        oauth_client = OAuthAPI(session=request.session)
        user = request.user.get_with_api_data_and_assos(oauth_client)
        return user.is_manager_of(asso_id)

    def has_object_permission(self, request, view, obj) -> bool:
        # No need for object permission
        return True


def check_order_ownership(request, view, obj):
    if isinstance(obj, Order):
        owner = obj.owner
    elif isinstance(obj, OrderLine):
        owner = obj.order.owner
    elif isinstance(obj, OrderLineItem):
        owner = obj.orderline.order.owner
    elif isinstance(obj, OrderLineField):
        owner = obj.orderlineitem.orderline.order.owner
    return owner == request.user

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
