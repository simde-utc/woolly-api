from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view


@api_view(['GET'])
def api_root(request, format=None):
    """
    Defines the clickable links displayed on the server endpoint.
    All the reachable endpoints don't appear here
    """
    kwargs = { 'request': request, 'format': format }
    return Response({
        # Login & Users
        'login':           reverse('login',                **kwargs),
        'me':              reverse('me',                   **kwargs),
        'users':           reverse('users-list',           **kwargs),
        'usertypes':       reverse('usertypes-list',       **kwargs),
        'associations':    reverse('associations-list',    **kwargs),

        # Sales & Item
        'sales':           reverse('sales-list',           **kwargs),
        'itemgroups':      reverse('itemgroups-list',      **kwargs),
        'items':           reverse('items-list',           **kwargs),

        # Orders
        'orders':          reverse('orders-list',          **kwargs),
        'orderlines':      reverse('orderlines-list',      **kwargs),

        # Fields
        'fields':          reverse('fields-list',          **kwargs),
        'itemfields':      reverse('itemfields-list',      **kwargs),
        'orderlinefields': reverse('orderlinefields-list', **kwargs),
        'orderlineitems':  reverse('orderlineitems-list',  **kwargs),

        # TODO PaymentMethods
        # 'paymentmethods':  reverse('paymentmethods-list',  **kwargs),
    })
