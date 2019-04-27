from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view


@api_view(['GET'])
def api_root(request, format=None):
	"""
	Defines the clickable links displayed on the server endpoint.
	All the reachable endpoints don't appear here
	"""
	return Response({
		# Login & Users
		'login':              reverse('auth.login',                request=request, format=format),
		'me':                 reverse('auth.me',                   request=request, format=format),
		'users':              reverse('users-list',                request=request, format=format),
		'usertypes':          reverse('usertypes-list',            request=request, format=format),

		# Associations
		'associations':       reverse('associations-list',         request=request, format=format),
		'associationmembers': reverse('associationmembers-list',   request=request, format=format),

		# Sales & Item
		'sales':              reverse('sales-list',                request=request, format=format),
		'itemgroups':         reverse('itemgroups-list',           request=request, format=format),
		'items':              reverse('items-list',                request=request, format=format),

		# Orders
		'orders':             reverse('orders-list',               request=request, format=format),
		'orderlines':         reverse('orderlines-list',           request=request, format=format),

		# Fields
		'fields':             reverse('fields-list',               request=request, format=format),
		# INUTILE ??
		'itemfields':         reverse('itemfields-list',           request=request, format=format),
		'orderlinefields':    reverse('orderlinefields-list',      request=request, format=format),
		'orderlineitems':     reverse('orderlineitems-list',       request=request, format=format),

		# PaymentMethods
		# 'paymentmethods':   reverse('paymentmethods-list',     request=request, format=format),
	})
	