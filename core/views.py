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
		'login': 				reverse('auth.login', 				request=request, format=format),
		'users': 				reverse('user-list', 				request=request, format=format),
		'usertypes': 			reverse('usertype-list', 			request=request, format=format),

		# Associations
		'associations': 		reverse('association-list', 		request=request, format=format),
		'associationmembers': 	reverse('associationmember-list', 	request=request, format=format),

		# Sales & Item
		'sales': 				reverse('sale-list', 				request=request, format=format),
		'itemgroups':			reverse('itemgroup-list', 			request=request, format=format),
		'items': 				reverse('item-list', 				request=request, format=format),

		# Orders
		'orders': 				reverse('order-list', 				request=request, format=format),
		'orderlines': 			reverse('orderline-list', 			request=request, format=format),

		# Fields
		'fields': 				reverse('field-list', 				request=request, format=format),
		# INUTILE ??
		'itemfields': 			reverse('itemfield-list', 			request=request, format=format),
		'orderlinefields': 		reverse('orderlinefield-list', 		request=request, format=format),
		'orderlineitems': 		reverse('orderlineitem-list', 		request=request, format=format),

		# PaymentMethods
		# 'paymentmethods': 		reverse('paymentmethod-list', 		request=request, format=format),
	})