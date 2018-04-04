from rest_framework import viewsets
from rest_framework import permissions
from django.http import HttpResponse, JsonResponse
from django.db.models import F

import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import detail_route, list_route
from rest_framework import permissions
from .permissions import IsOwner

from rest_framework_json_api.views import RelationshipView

from .models import (
	Item, ItemSpecifications, Association, Sale, Order, OrderLine,
	PaymentMethod, AssociationMember
)
from .serializers import (
	ItemSerializer, ItemSpecificationsSerializer, AssociationSerializer,
	OrderSerializer, OrderLineSerializer, SaleSerializer,
	PaymentMethodSerializer, AssociationMemberSerializer
)
from payutc import payutc

# TODO : Déplacer dans core ?
@api_view(['GET'])
def api_root(request, format=None):
	"""
		Defines the clickable links displayed on the server endpoint.
		All the reachable endpoints don't appear here
	"""
	return Response({
		'users': reverse('user-list', request=request, format=format),
		'woollyusertypes': reverse('usertype-list', request=request, format=format),
		'associations': reverse('association-list', request=request, format=format),
		'associationmembers': reverse('associationmember-list', request=request, format=format),
		'sales': reverse('sale-list', request=request, format=format),
		'items': reverse('item-list', request=request, format=format),
		'itemSpecifications': reverse('itemSpecification-list', request=request, format=format),
		'orders': reverse('order-list', request=request, format=format),
		'orderlines': reverse('orderline-list', request=request, format=format),
		'paymentmethods': reverse('paymentmethod-list', request=request, format=format),
	})


class AssociationViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the association view
	"""
	queryset = Association.objects.all()
	serializer_class = AssociationSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset.filter(associationmembers__woollyUser=self.request.user_pk)

		if 'associationmember_pk' in self.kwargs:
			associationmember_pk = self.kwargs['associationmember_pk']
			queryset = Association.objects.all().filter(associationmembers__pk=associationmember_pk)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = Association.objects.all().filter(associationmembers__woollyUser=user_pk)

		return queryset


class AssociationMemberViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior link to the association member view
	"""
	queryset = AssociationMember.objects.all()
	serializer_class = AssociationMemberSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(
			woollyUser_id=self.request.user.id,
			association_id=self.kwargs['association_pk'],
		)

	def get_queryset(self):
		queryset = self.queryset

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(woollyUser__pk=user_pk)

		if 'association_pk' in self.kwargs:
			association_pk = self.kwargs['association_pk']
			queryset = queryset.filter(association__pk=association_pk)

		return queryset


class PaymentMethodViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the payment method view
	"""
	queryset = PaymentMethod.objects.all()
	serializer_class = PaymentMethodSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset
		if 'sale_pk' in self.kwargs:
			sale_pk = self.kwargs['sale_pk']
			queryset = queryset.filter(sales__pk=sale_pk)

		return queryset


class OrderViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the order CRUD
	"""
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = (permissions.IsAuthenticated, IsOwner,)

	def perform_create(self, serializer):
		# Get the customized Orderlines through JSON
		# import pdb; pdb.set_trace()
		validate_items = []
		if 'lines' in self.request.data:
			if len(self.request.data['lines']) > 0:
				for line in self.request.data['lines']:
					# Check the quantity of each item
					# TO DO : Call the check quantity function

					# If there is enough stock, add the article
					# to the validate items list
					validate_items.append(line)
		print(self.request.session)
		print(self.request.user)
		# Create the order
		serializer.save(
			
			owner=self.request.user
		)

		if len(validate_items):
			# Get the new order ID
			order_id = serializer.data['id']

			# Then create the orderlines and link them to the order
			for line in validate_items:
				q = OrderLine()
				q.item = Item.objects.all().get(pk=line['item'])
				q.order = Order.objects.all().get(pk=order_id)
				q.quantity = line['quantity']

				q.save()


	def get_queryset(self):
		queryset = self.queryset.filter(owner=self.request.user)

		if 'woollyuser_pk' in self.kwargs:
			woollyuser_pk = self.kwargs['woollyuser_pk']
			queryset = queryset.filter(owner__pk=woollyuser_pk)

		return queryset


class OrderLineViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the Orderline view
	"""
	queryset = OrderLine.objects.all()
	serializer_class = OrderLineSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(order_id=self.kwargs['order_pk'])
		queryset2 = OrderLine.objects.all().filter(order__pk=self.kwargs['order_pk'])
		idarticle = queryset2.values()[0]['id']
		queryset3 = ItemSpecifications.objects.all().filter(item__pk=idarticle)
		orderlineId = queryset2.values()[0]['id']
		funId = queryset3.values()[0]['fun_id']
		itemId = queryset3.values()[0]['nemopay_id']
		quantity = queryset3.values()[0]['quantity']
		queryset3.update(quantity=F('quantity')-1)
		data = json.dumps([[itemId,quantity]])
		login = self.request.user.login
		return requests.get('http://localhost:8000/payutc/createTransaction?mail='+login+'&funId='+funId+"&orderlineId="+str(orderlineId),data=data)
		# def perform_create(self, serializer):
		# 	serializer.save()

	def get_queryset(self):
		queryset = self.queryset.filter(order__owner=self.request.user)
		if 'order_pk' in self.kwargs:
			order_pk = self.kwargs['order_pk']
			queryset = OrderLine.objects.all().filter(order__pk=order_pk)

		return queryset


class SaleViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the sale view
	"""
	serializer_class = SaleSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(
			association_id=self.kwargs['association_pk'],
			paymentmethod_id=self.kwargs['paymentmethod_pk']
		)

	def get_queryset(self):
		queryset = Sale.objects.all().filter(
			items__itemspecifications__woolly_user_type__name=self.request.user.woollyusertype.name)

		# if this viewset is accessed via the 'association-detail' route,
		# it wll have been passed the `association_pk` kwarg and the queryset
		# needs to be filtered accordingly
		if 'association_pk' in self.kwargs:
			association_pk = self.kwargs['association_pk']
			queryset = Sale.objects.all().filter(association__pk=association_pk)

		# TO DO : Remove this in order not to display all the sales link
		# to a payment method on every Sale JSON
		if 'payment_pk' in self.kwargs:
			payment_pk = self.kwargs['payment_pk']
			queryset = Sale.objects.all().filter(paymentmethods__pk=payment_pk)

		return queryset


class ItemSpecificationsViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the item specifications view
	"""
	queryset = ItemSpecifications.objects.all()
	serializer_class = ItemSpecificationsSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(
			item_id=self.kwargs['item_pk']
		)

	def get_queryset(self):
		queryset = self.queryset
		if 'item_pk' in self.kwargs:
			item_pk = self.kwargs['item_pk']
			queryset = queryset.filter(item__pk=item_pk)

		return queryset


class ItemViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the item interactions
	"""
	queryset = Item.objects.all()
	serializer_class = ItemSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		if 'orderline_pk' in self.kwargs:
			serializer.save(
				sale_id=self.kwargs['sale_pk']
			)

		if 'orderline_pk' in self.kwargs:
			serializer.save(
				sale_id=self.kwargs['orderline_pk']
			)

	def get_queryset(self):
		queryset = self.queryset.filter(
			itemspecifications__woolly_user_type__name=self.request.user.woollyusertype.name)

		if 'sale_pk' in self.kwargs:
			sale_pk = self.kwargs['sale_pk']
			queryset = queryset.filter(sale__pk=sale_pk)

		if 'orderline_pk' in self.kwargs:
			orderline_pk = self.kwargs['orderline_pk']
			queryset = queryset.filter(orderlines__pk=orderline_pk)

		return queryset


class OrderLineItemViewSet(viewsets.ModelViewSet):
	"""
		Defines the view which display the items of an orderline
	"""
	queryset = Item.objects.all()
	serializer_class = ItemSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(
			sale_id=self.kwargs['orderline_pk']
		)

	def get_queryset(self):
		queryset = self.queryset
		if 'orderline_pk' in self.kwargs:
			orderline_pk = self.kwargs['orderline_pk']
			queryset = queryset.filter(orderlines__pk=orderline_pk)

		return queryset


class OrderRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the orders related links
	"""
	queryset = Order.objects


class OrderLineRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLine.objects


class ItemRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the items related links
	"""
	queryset = Item.objects


class SaleRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the sales related links
	"""
	queryset = Sale.objects


class AssociationMemberRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the association members related links
	"""
	queryset = AssociationMember.objects


class ItemSpecificationsRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the item specifications related links
	"""
	queryset = ItemSpecifications.objects


class AssociationRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the associations related links
	"""
	queryset = Association.objects


class PaymentMethodRelationshipView(RelationshipView):
	"""
		Required by JSON API to display the payment methods related links
	"""
	queryset = PaymentMethod.objects

class WoollyUserViewSet(viewsets.ModelViewSet):
	"""
		Defines the behavior of the association view
	"""
	queryset = Association.objects.all()
	serializer_class = AssociationSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		queryset = self.queryset.filter(associationmembers__woollyUser=self.request.user)

		if 'associationmember_pk' in self.kwargs:
			associationmember_pk = self.kwargs['associationmember_pk']
			queryset = Association.objects.all().filter(associationmembers__pk=associationmember_pk)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = Association.objects.all().filter(associationmembers__woollyUser=user_pk)

		return queryset
