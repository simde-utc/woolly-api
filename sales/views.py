import requests
import json

from rest_framework import viewsets
from rest_framework_json_api.views import RelationshipView
from django.db.models import F

from rest_framework import permissions
from .permissions import *
from core.permissions import *
from .models import *
from .serializers import *

from payutc import payutc

# queryset .all() ??????

# ============================================
# 	Association
# ============================================

class AssociationViewSet(viewsets.ModelViewSet):
	"""
	Defines the behavior of the association view
	"""
	queryset = Association.objects.all()
	serializer_class = AssociationSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def get_queryset(self):
		# print(self.request.user)
		# queryset = self.queryset.filter(associationmembers__user=self.request.user_pk)
		"""
		if 'associationmember_pk' in self.kwargs:
			associationmember_pk = self.kwargs['associationmember_pk']
			queryset = Association.objects.all().filter(associationmembers__pk=associationmember_pk)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = Association.objects.all().filter(associationmembers__user=user_pk)
		"""
		return self.queryset

class AssociationRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the associations related links
	"""
	queryset = Association.objects


class AssociationMemberViewSet(viewsets.ModelViewSet):
	"""
	Defines the behavior link to the association member view
	"""
	queryset = AssociationMember.objects.all()
	serializer_class = AssociationMemberSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		serializer.save(
			user_id = self.request.user.id,
			association_id = self.kwargs['association_pk'],
		)

	def get_queryset(self):
		queryset = self.queryset

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(user__pk=user_pk)

		if 'association_pk' in self.kwargs:
			association_pk = self.kwargs['association_pk']
			queryset = queryset.filter(association__pk=association_pk)

		return queryset

class AssociationMemberRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the association members related links
	"""
	queryset = AssociationMember.objects


# ============================================
# 	Sale
# ============================================

class SaleViewSet(viewsets.ModelViewSet):
	"""
	Defines the behavior of the sale view
	"""
	serializer_class = SaleSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def perform_create(self, serializer):
		serializer.save(
			association_id=self.kwargs['association_pk'],
			paymentmethod_id=self.kwargs['paymentmethod_pk']
		)

	def get_queryset(self):
		queryset = Sale.objects.all()
					# .filter(items__itemspecifications__user_type__name=self.request.user.usertype.name)
					# TODO filtrer par date ?

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

class SaleRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the sales related links
	"""
	queryset = Sale.objects


class PaymentMethodViewSet(viewsets.ModelViewSet):
	# TODO a virer
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

class PaymentMethodRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the payment methods related links
	"""
	queryset = PaymentMethod.objects


# ============================================
# 	Item
# ============================================

class ItemGroupViewSet(viewsets.ModelViewSet):
	"""
	Defines the behavior of the itemGroup interactions
	"""
	queryset = ItemGroup.objects.all()
	serializer_class = ItemGroupSerializer
	permission_classes = (permissions.IsAuthenticated,)

class ItemGroupRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the itemGroups related links
	"""
	queryset = ItemGroup.objects


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
			itemspecifications__user_type__name=self.request.user.usertype.name)

		if 'sale_pk' in self.kwargs:
			sale_pk = self.kwargs['sale_pk']
			queryset = queryset.filter(sale__pk=sale_pk)

		if 'orderline_pk' in self.kwargs:
			orderline_pk = self.kwargs['orderline_pk']
			queryset = queryset.filter(orderlines__pk=orderline_pk)

		return queryset

class ItemRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the items related links
	"""
	queryset = Item.objects


# ============================================
# 	Order & OrderLine
# ============================================

class OrderViewSet(viewsets.ModelViewSet):
	"""
	Defines the behavior of the order CRUD
	"""
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = (permissions.IsAuthenticated, IsOwner,)

	"""
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
	"""


	def get_queryset(self):
		queryset = self.queryset.filter(owner=self.request.user)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(owner__pk=user_pk)

		return queryset

class OrderRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the orders related links
	"""
	queryset = Order.objects


class OrderLineViewSet(viewsets.ModelViewSet):
	"""
	Defines the behavior of the Orderline view
	"""
	queryset = OrderLine.objects.all()
	serializer_class = OrderLineSerializer
	permission_classes = (permissions.IsAuthenticated,)

	"""
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
	"""

class OrderLineRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLine.objects


# ============================================
# 	Field, ItemField & OrderLineField
# ============================================

class FieldViewSet(viewsets.ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = Field.objects.all()
	serializer_class = FieldSerializer
	permission_classes = (IsAdminOrReadOnly,)

class FieldRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = Field.objects


class ItemFieldViewSet(viewsets.ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = ItemField.objects.all()
	serializer_class = ItemFieldSerializer
	permission_classes = (IsAdminOrReadOnly,)

class ItemFieldRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = ItemField.objects


class OrderLineFieldViewSet(viewsets.ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = OrderLineField.objects.all()
	serializer_class = OrderLineField
	permission_classes = (permissions.IsAuthenticated,)

	"""
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
	"""

class OrderLineFieldRelationshipView(RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLineField.objects

