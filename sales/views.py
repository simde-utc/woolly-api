from rest_framework_json_api import views
from rest_framework.response import Response
from rest_framework import permissions, status
from django.http import JsonResponse
from django.urls import reverse

from core.permissions import *
from .models import *
from .serializers import *
from .permissions import *


# ============================================
# 	Association
# ============================================

class AssociationViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the association view
	"""
	queryset = Association.objects.all()
	serializer_class = AssociationSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	"""
	def get_queryset(self):
		# print(self.request.user)
		# queryset = self.queryset.filter(associationmembers__user=self.request.user_pk)
		if 'associationmember_pk' in self.kwargs:
			associationmember_pk = self.kwargs['associationmember_pk']
			queryset = Association.objects.all().filter(associationmembers__pk=associationmember_pk)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = Association.objects.all().filter(associationmembers__user=user_pk)
		return queryset
	"""

class AssociationRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the associations related links
	"""
	queryset = Association.objects

class AssociationMemberViewSet(views.ModelViewSet):
	"""
	Defines the behavior link to the association member view
	"""
	queryset = AssociationMember.objects.all()
	serializer_class = AssociationMemberSerializer
	permission_classes = (IsAdmin,)	# TODO V2 : bloquer pour l'instant

	"""
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
	"""

class AssociationMemberRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the association members related links
	"""
	queryset = AssociationMember.objects


# ============================================
# 	Sale
# ============================================

class SaleViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the sale view
	"""
	serializer_class = SaleSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	def perform_create(self, serializer):
		serializer.save(
			association_id=self.kwargs['association_pk'],
			# paymentmethod_id=self.kwargs['paymentmethod_pk']
		)

	def get_queryset(self):
		queryset = Sale.objects.all()
					# .filter(items__itemspecifications__user_type__name=self.request.user.usertype.name)
					# TODO filtrer par date ?

		queryset = queryset.filter(is_active=True)
		# TODO V2 : filtering
		# filters = ('active', )
		# filterQuery = self.request.query_params.get('filterQuery', None)
		# if filterQuery is not None:
			# queryset = queryset.filter()
			# pass

		# Association detail route
		if 'association_pk' in self.kwargs:
			association_pk = self.kwargs['association_pk']
			queryset = queryset.filter(association__pk=association_pk)

		return queryset

class SaleRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the sales related links
	"""
	queryset = Sale.objects


class PaymentMethodViewSet(views.ModelViewSet):
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

class PaymentMethodRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the payment methods related links
	"""
	queryset = PaymentMethod.objects


# ============================================
# 	Item
# ============================================

class ItemGroupViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the itemGroup interactions
	"""
	queryset = ItemGroup.objects.all()
	serializer_class = ItemGroupSerializer
	permission_classes = (permissions.IsAuthenticated,)

class ItemGroupRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the itemGroups related links
	"""
	queryset = ItemGroup.objects


class ItemViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the item interactions
	"""
	queryset = Item.objects.all()
	serializer_class = ItemSerializer
	# permission_classes = (permissions.IsAuthenticated,)

	def perform_create(self, serializer):
		if 'orderline_pk' in self.kwargs:
			serializer.save(
				sale_id=self.kwargs['sale_pk']
			),
			serializer.save(
				sale_id=self.kwargs['orderline_pk']
			)

	def get_queryset(self):
		queryset = self.queryset.filter()

		if 'sale_pk' in self.kwargs:
			sale_pk = self.kwargs['sale_pk']
			queryset = queryset.filter(sale__pk=sale_pk)

		if 'orderline_pk' in self.kwargs:
			orderline_pk = self.kwargs['orderline_pk']
			queryset = queryset.filter(orderlines__pk=orderline_pk)

		return queryset


class ItemRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the items related links
	"""
	queryset = Item.objects


# ============================================
# 	Order & OrderLine
# ============================================

class OrderViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the order CRUD
	"""
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = (permissions.IsAuthenticated, IsOwner)
	validStatusList = [OrderStatus.ONGOING.value, OrderStatus.AWAITING_VALIDATION.value, OrderStatus.NOT_PAYED.value]

	def create(self, request):
		"""
		Find or create Order on POST
		"""
		try:
			# TODO ajout de la limite de temps
			order = Order.objects \
				.filter(status__in=self.validStatusList) \
				.get(sale=request.data['sale']['id'], owner=request.user.id)

			serializer = OrderSerializer(order)
			httpStatus = status.HTTP_200_OK
		except Order.DoesNotExist as err:
			# Configure Order
			serializer = OrderSerializer(data = {
				'sale': request.data['sale'],
				'owner': {
					'id': request.user.id,
					'type': 'users'
				},
				'orderlines': []
			})
			serializer.is_valid(raise_exception=True)
			self.perform_create(serializer)
			httpStatus = status.HTTP_201_CREATED

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=httpStatus, headers=headers)


	def get_queryset(self):
		# queryset = self.queryset.filter(owner=self.request.user)
		queryset = self.queryset

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(owner__pk=user_pk)

		return queryset

class OrderRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orders related links
	"""
	queryset = Order.objects


class OrderLineViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the Orderline view
	"""
	queryset = OrderLine.objects.all()
	serializer_class = OrderLineSerializer
	permission_classes = (permissions.IsAuthenticated,)

	def create(self, request):
		try:
			order = Order.objects.get(pk=request.data['order']['id'])
		except Order.DoesNotExist as err:
			msg = "Impossible de trouver la commande."
			return errorResponse(msg, [msg], status.HTTP_404_NOT_FOUND)
		if order.status != OrderStatus.ONGOING.value:
			msg = "La commande n'accepte plus d'ajout."
			return errorResponse(msg, [msg], status.HTTP_400_BAD_REQUEST)

		try:
			# TODO ajout de la limite de temps
			orderline = OrderLine.objects.get(order=request.data['order']['id'], item=request.data['item']['id'])
			serializer = OrderLineSerializer(orderline, data={'quantity': request.data['quantity']}, partial=True)
		except OrderLine.DoesNotExist as err:
			# Configure Order
			serializer = self.get_serializer(data={
				'order': request.data['order'],
				'item': request.data['item'],
				'quantity': request.data['quantity']
			})
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

class OrderLineRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLine.objects

# ============================================
# 	Field, ItemField & OrderLineField
# ============================================

class FieldViewSet(views.ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = Field.objects.all()
	serializer_class = FieldSerializer
	permission_classes = (IsAdminOrReadOnly,)

class FieldRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = Field.objects


class ItemFieldViewSet(views.ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = ItemField.objects.all()
	serializer_class = ItemFieldSerializer
	permission_classes = (IsAdminOrReadOnly,)

class ItemFieldRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = ItemField.objects


class OrderLineFieldViewSet(views.ModelViewSet):
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

class OrderLineFieldRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLineField.objects

