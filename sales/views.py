import requests
import json

# from django.db.models import F
from rest_framework_json_api import views
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import permissions, status

from core.permissions import *
from .models import *
from .serializers import *
from .permissions import *

from payutc.payutc import Payutc
from woolly_api.settings import PAYUTC_KEY
from rest_framework.decorators import *
from authentication.auth import JWTAuthentication

# queryset .all() ??????

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

	def create(self, request):
		"""
		Find or create Order on POST
		"""
		try:
			# TODO ajout de la limite de temps
			order = Order.objects.get(sale=request.data['sale']['id'], owner=request.user.id)
			serializer = OrderSerializer(order)
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

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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




# ----------------------------------------------------------

@api_view(['GET'])
@authentication_classes((JWTAuthentication,))
@permission_classes((permissions.IsAuthenticated, IsOwner))
def pay(request, pk):
	# Récupération de l'Order
	try:
		# TODO ajout de la limite de temps
		order = Order.objects.filter(owner=request.user).get(pk=pk)
	except Order.DoesNotExist as e:
		return Response({'message': e}, status=status.HTTP_400_BAD_REQUEST)

	# Retrieve orderlines
	orderlines = order.orderlines.filter(quantity__gt=0).all()

	# TODO Verifications
	errors = verifyOrder(order, request.user)

	# Create Payutc params
	payutc = Payutc({ 'app_key': PAYUTC_KEY })
	params = {
		# 'items': [],
		'mail': request.user.email,
		'return_url': request.GET.get('return_url', None),
		'fun_id': order.sale.association.fun_id,
		'callback_url': request.GET.get('return_url', None)
	}

	# Add items
	# TODO perf
	itemsArray = []
	for orderline in orderlines:
		itemsArray.append([int(orderline.item.nemopay_id), orderline.quantity])
	params['items'] = str(itemsArray)

	# Create transaction
	transaction = payutc.createTransaction(params)
	print(transaction)
	if 'error' in transaction:
		return Response({'message': transaction['error']['message']}, status=status.HTTP_400_BAD_REQUEST)

	# Save transaction info
	order.tra_id = transaction['tra_id']
	order.save()

	# TODO Redirect to transaction url
	return JsonResponse({ 'url': transaction['url'] }, status=status.HTTP_200_OK)
	# return Response(OrderSerializer(order), status=status.HTTP_200_OK)


def verifyOrder(order, user):
	# Error bag to store all error messages
	errors = list()
	# OrderStatus considered as not canceled
	statusList = [OrderStatus.AWAITING_VALIDATION, OrderStatus.VALIDATED, OrderStatus.NOT_PAYED, OrderStatus.PAYED]

	# Fetch orders made by the user
	userOrders = Order.objects \
					.filter(user__pk=user.pk, sale__pk=order.sale.pk, status__in=statusList) \
					.exclude(pk=order.pk)
	# Count quantity bought by user
	quantityByUser = dict()
	quantityByUserTotal = 0
	for orderline in userOrders.orderlines:
		quantityByUser[orderline.item.pk] = orderline.quantity + quantityByUser.get(orderline.item.pk, 0)
		quantityByUserTotal += orderline.quantity
	# DEBUG
	print("userOrders", userOrders)
	print("quantityByUser", quantityByUser)
	print("quantityByUserTotal", quantityByUserTotal)

	# Fetch all orders of the sale
	saleOrders = Order.objects \
					.filter(sale__pk=order.sale.pk, status__in=statusList) \
					.exclude(pk=order.pk)
	# Count quantity bought by sale
	quantityBySale = dict()
	quantityBySaleTotal = 0
	for orderline in saleOrders.orderlines:
		quantityBySale[orderline.item.pk] = orderline.quantity + quantityBySale.get(orderline.item.pk, 0)
		quantityBySaleTotal += orderline.quantity
	# DEBUG
	print("saleOrders", saleOrders)
	print("quantityBySale", quantityBySale)
	print("quantityBySaleTotal", quantityBySaleTotal)


	# Verify quantity left by sale
	if order.max_item_quantity != None:
		if order.max_item_quantity < quantityBySaleTotal + quantityByUserTotal:
			errors.append("Il ne reste moins de {} items pour cette vente." \
				.format(order.max_item_quantity - quantityBySaleTotal))


	# Check for each orderlines
	for orderline in order.orderlines:

		# Verif max_per_user // quantity
		if orderline.quantity > orderline.item.max_per_user:
			errors.append("Vous ne pouvez prendre que {} {} par personne." \
				.format(orderline.item.max_per_user, orderline.item.name))

		# Verif max_per_user // user orders
		if quantityBoughtByUser[orderline.item.pk] + orderline.quantity > orderline.item.max_per_user:
			errors.append("Vous avez déjà pris {} {} sur un total de {} par personne." \
				.format(quantityBoughtByUser[orderline.item.pk], orderline.item.name, orderline.item.max_per_user))

		# Verify quantity left // sale orders
		if orderline.item.quantity != None:
			if orderline.item.quantity < quantityBySale[orderline.item.pk] + orderline.quantity:
				errors.append("Vous avez déjà pris {} {} sur un total de {} par personne." \
					.format(quantityBySale[orderline.item.pk], orderline.item.name, orderline.item.max_per_user))

		# Verif cotisant
		if orderline.item.usertype.name == UserType.COTISANT:
			if user.usertype.name != UserType.COTISANT:
				errors.append("Vous devez être {} pour prendre {}.".format(UserType.COTISANT, orderline.item.name))

		# Verif non cotisant (ultra sale mais flemme)
		if orderline.item.usertype.name == UserType.NON_COTISANT:
			if user.usertype.name == UserType.EXTERIEUR:
				errors.append("Vous devez être {} pour prendre {}.".format("UTCéen", orderline.item.name))

	return errors
