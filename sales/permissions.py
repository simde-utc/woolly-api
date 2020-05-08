from typing import Any

from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed

from core.exceptions import InvalidRequest
from authentication.oauth import OAuthAPI
from .models import (
    Association, Sale, Item, ItemGroup, ItemField,
    Order, OrderLine, OrderLineItem, OrderLineField
)


def get_url_param(request, name: str) -> Any:
    param_request = request.data.get(name)
    if param_request:
        return param_request
    else:
        raise InvalidRequest(f"Could not retrieve parameter '{name}' from request")

    # TODO Needed ?
    """
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
    """


def get_related_model(Model, pk, *related) -> Any:
    try:
        query = Model.objects
        if related:
            query = query.select_related(*related)
        return query.get(pk=pk)
    except Model.DoesNotExist:
        raise InvalidRequest(f"Could not retrieve related {Model.__name__}")


def get_related_asso_id(request, view) -> str:
    Model = view.queryset.model
    if Model not in { Association, Sale, Item, ItemGroup, ItemField }:
        raise NotImplementedError(f"Model {Model.__name__} is not managed")

    if view.action is None:
        raise MethodNotAllowed(request.method)

    hasPk = 'pk' in view.kwargs
    pk = view.kwargs.get('pk')

    if Model is Association:
        if view.action in {'create', 'delete'}:
            return False
        else:
            return pk

    elif Model is Sale:
        if hasPk:
            return get_related_model(Sale, pk).association_id
        else:
            return get_url_param(request, 'association')

    elif Model is Item or Model is ItemGroup:
        if hasPk:
            return get_related_model(Model, pk, 'sale').sale.association_id
        else:
            sale_pk = get_url_param(request, 'sale')
            return get_related_model(Sale, sale_pk).association_id

    elif Model is ItemField:
        if hasPk:
            return get_related_model(ItemField, pk, 'item__sale').item.sale.association_id
        else:
            item_pk = get_url_param(request, 'item')
            return get_related_model(Item, item_pk, 'sale').sale.association_id

    raise InvalidRequest("Could not retrieve related Association")


def check_is_manager(request, view) -> bool:

    # Need authenticated user
    if not request.user.is_authenticated:
        return False

    # Get the related association
    asso_id = get_related_asso_id(request, view)

    # Check that the association is real
    if not Association.objects.filter(pk=asso_id).exists():
        raise InvalidRequest(f"Could not retrieve association '{asso_id}'")

    # Get user's associations and check if is manager
    oauth_client = OAuthAPI(session=request.session)
    user = request.user.get_with_api_data_and_assos(oauth_client)
    return user.is_manager_of(asso_id)


def check_order_ownership(request, view, obj) -> bool:
    """
    Check that the owner of the Order and the user match
    """
    user = request.user
    Model = type(obj)

    if Model is Order:
        return user == obj.owner
    elif Model is OrderLine:
        return user == obj.order.owner
    elif Model is OrderLineItem:
        return user == obj.orderline.order.owner
    elif Model is OrderLineField:
        return user == obj.orderlineitem.orderline.order.owner

    raise NotImplementedError(f"Cannot check owner of object {Model.__name__}")


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Allow read for everyone and check that the user
    is manager of the Association related to the target resource

    Used for Association, Sale, ItemGroup, Item, ItemField
    """

    def has_permission(self, request, view) -> bool:

        # Allow admin
        if request.user.is_authenticated and request.user.is_admin:
            return True

        # Allow read only
        if request.method in permissions.SAFE_METHODS:
            return True

        # Need to be manager
        return check_is_manager(request, view)

    def has_object_permission(self, request, view, obj) -> bool:
        # No need for object permission
        return True


class IsOwnerOrManagerReadOnly(permissions.BasePermission):
    """
    Check that a user is owner of the order for modification
    or manager of the Association for read only.
    Allow creation for authenticated user.

    Used for Order, OrderLine
    """

    def has_permission(self, request, view) -> bool:

        # Need to be authenticated
        if not request.user.is_authenticated:
            return False

        # Allow admin
        if request.user.is_admin:
            return True

        # Allow read only for manager
        if request.method in permissions.SAFE_METHODS and check_is_manager(request, view):
            return True

        # Allow creation
        if view.action == 'create':
            return True

        # Pass for object action
        if view.action in {'retrieve', 'update', 'partial_update', 'destroy'}:
            return True

        return False

    def has_object_permission(self, request, view, obj) -> bool:

        # Allow admin
        if request.user.is_admin:
            return True

        # Allow read only for manager
        if request.method in permissions.SAFE_METHODS and check_is_manager(request, view):
            return True

        # Need to be owner to modify
        return check_order_ownership(request, view, obj)


class CanOnlyReadOrUpdate(permissions.BasePermission):
    """
    Can only read or update
    """

    def has_permission(self, request, view) -> bool:
        return bool(view.action)

    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_admin \
            or view.action in {'retrieve', 'partial_update', 'update'}
