import base64
from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from authentication.oauth import OAuthAuthentication
from core.utils import render_to_pdf, data_to_qrcode
from core.viewsets import ModelViewSet, APIModelViewSet
from core.permissions import IsAdminOrReadOnly
from sales.permissions import (
	IsManagerOrReadOnly, IsOrderOwnerOrAdmin,
	IsOrderOwnerReadOnlyOrAdmin, IsOrderOwnerReadUpdateOrAdmin
)
from sales.exceptions import OrderValidationException
from sales.models import (
	Association, Sale, ItemGroup, Item,
	OrderStatus, Order, OrderLine, OrderLineItem,
	Field, ItemField, OrderLineField
)
from sales.serializers import (
	AssociationSerializer, SaleSerializer, ItemGroupSerializer, ItemSerializer,
	OrderSerializer, OrderLineSerializer, OrderLineItemSerializer,
	FieldSerializer, ItemFieldSerializer, OrderLineFieldSerializer,
)


# ============================================
# 	Association
# ============================================

class AssociationViewSet(APIModelViewSet):
	"""
	Defines the behavior of the association view
	"""
	queryset = Association.objects.all()
	serializer_class = AssociationSerializer
	permission_classes = (IsManagerOrReadOnly,)

	def get_sub_urls_filters(self, queryset) -> dict:
		"""
		Override of core.viewsets.ModelViewSet for owner-user correspondance
		"""
		filters = super().get_sub_urls_filters(queryset)
		# Remove user__pk because it is not used for model lookup
		filters.pop('user__pk', None)
		return filters

# ============================================
# 	Sale
# ============================================

class SaleViewSet(ModelViewSet):
	"""
	Defines the behavior of the sale view
	"""
	queryset = Sale.objects.all()
	serializer_class = SaleSerializer
	permission_classes = (IsManagerOrReadOnly,)

	# TODO Check for association in data or url for create/update

	def get_queryset(self):
		queryset = super().get_queryset()
		# .filter(items__itemspecifications__user_type__name=self.request.user.usertype.name)
		# TODO filtrer par date ?

		# queryset = queryset.filter(is_active=True, is_public=True)
		if not self.request.GET.get('include_inactive', False):
			queryset = queryset.filter(is_active=True)
		if 'pk' not in self.kwargs:
			queryset = queryset.filter(is_public=True)

		# TODO V2 : filtering
		# filters = ('active', )
		# filterQuery = self.request.GET.get('filterQuery', None)
		# if filterQuery is not None:
			# queryset = queryset.filter()
			# pass

		return queryset

# ============================================
# 	Item
# ============================================

class ItemGroupViewSet(ModelViewSet):
	"""
	Defines the behavior of the itemGroup interactions
	"""
	queryset = ItemGroup.objects.all()
	serializer_class = ItemGroupSerializer
	permission_classes = (IsManagerOrReadOnly,)

class ItemViewSet(ModelViewSet):
	"""
	Defines the behavior of the item interactions
	"""
	queryset = Item.objects.all()
	serializer_class = ItemSerializer
	permission_classes = (IsManagerOrReadOnly,)

	"""
	def perform_create(self, serializer):
		# TODO ????
		if 'sale_pk' in self.kwargs:
			serializer.save(
				sale_id=self.kwargs['sale_pk']
			)
		elif 'orderline_pk' in self.kwargs:
			serializer.save(
				sale_id=self.kwargs['orderline_pk']
			)
	"""

	def get_queryset(self):
		queryset = super().get_queryset()

		if not self.request.GET.get('include_inactive', False):
			queryset = queryset.filter(is_active=True)

		if 'sale_pk' in self.kwargs:
			sale_pk = self.kwargs['sale_pk']
			queryset = queryset.filter(sale__pk=sale_pk)

		if 'orderline_pk' in self.kwargs:
			orderline_pk = self.kwargs['orderline_pk']
			queryset = queryset.filter(orderlines__pk=orderline_pk)

		return queryset

# ============================================
# 	Order & OrderLine
# ============================================

class OrderViewSet(ModelViewSet):
	"""
	Defines the behavior of the Order CRUD

	TODO: update status if not stable
	"""
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = (IsOrderOwnerOrAdmin,)

	def get_sub_urls_filters(self, queryset) -> dict:
		filters = super().get_sub_urls_filters(queryset)
		if 'user__pk' in filters:
			filters['owner__pk'] = filters.pop('user__pk')
		return filters

	def get_queryset(self):
		queryset = super().get_queryset()

		# Get params
		user = self.request.user
		only_owner = not self.query_params_is_true('all')

		# Admins see everything
		# Otherwise automatically filter to only those owned by the user
		if only_owner or not user.is_admin:
			queryset = queryset.filter(owner=user)

		return queryset

	def get_object(self) -> Order:
		"""
		Try to update order status if unstable
		"""
		order = super().get_object()
		if order.status not in OrderStatus.STABLE_LIST.value:
			order.update_status()
		return order

	def create(self, request, *args, **kwargs):
		"""
		Find if user has a Buyable Order or create
		"""

		sale_pk = kwargs.get('sale_pk', request.data.get('sale'))
		try:
			# TODO ajout de la limite de temps
			order = self.get_queryset() \
				.filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
				.get(sale=sale_pk, owner=request.user.id)

			serializer = self.get_serializer(instance=order)
			httpStatus = status.HTTP_200_OK
		except Order.DoesNotExist:
			# Configure new Order
			serializer = OrderSerializer(data={
				'sale': sale_pk,
				'owner': request.user.id,
				'orderlines': [],
				'status': OrderStatus.ONGOING.value,
			})
			serializer.is_valid(raise_exception=True)
			self.perform_create(serializer)
			httpStatus = status.HTTP_201_CREATED

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=httpStatus, headers=headers)

	def destroy(self, request, *args, **kwargs):
		"""
		Doesn't destroy an order but set it as cancelled
		"""
		order = self.get_object()
		# TODO Check service status !!!
		if order.status in OrderStatus.CANCELLABLE_LIST.value:
			# TODO Add time
			order.status = OrderStatus.CANCELLED.value
			order.save()
			return Response(None, status=status.HTTP_204_NO_CONTENT)
		# elif order.status == OrderStatus.ONGOING.value:
		# 	# TODO A tester
		# 	order.delete()
		# 	return Response(None, status=status.HTTP_204_NO_CONTENT)
		else:
			raise OrderValidationException(
				f"La commande n'est pas annulable ({order.get_status_display()}).",
				'uncancellable_order'
			)

class OrderLineViewSet(ModelViewSet):
	"""
	Defines the behavior of the Orderline view
	"""
	queryset = OrderLine.objects.all()
	serializer_class = OrderLineSerializer
	permission_classes = (IsOrderOwnerOrAdmin,)

	def get_queryset(self):
		queryset = super().get_queryset()

		# Get params
		user = self.request.user
		only_owner = not self.query_params_is_true('all')

		# Admins see everything
		# Otherwise automatically filter to only those owned by the user
		if only_owner or not user.is_admin:
			queryset = queryset.filter(order__owner=user)

		return queryset

	def create(self, request, *args, **kwargs):
		"""
		Create an orderline attached to an order
		"""
		# Retrieve Order or fail
		order_pk = kwargs.get('order_pk', request.data.get('order'))
		order = Order.objects.get(pk=order_pk)

		# Check Order owner
		user = request.user
		if not (user.is_authenticated and user.is_admin or order.owner == user):
			raise PermissionDenied()

		# Check if Order is open
		if order.status != OrderStatus.ONGOING.value:
			raise OrderValidationException("La commande n'accepte plus de changement.", 'unchangable_order')

		item_pk = request.data.get('item')
		try:
			quantity = int(request.data.get('quantity'))
			assert quantity >= 0
		except (ValueError, AssertionError) as error:
			raise OrderValidationException(
				"La quantité d'article à acheter doit être positive ou nulle.",
				'order_quantity_null',
				status_code=status.HTTP_400_BAD_REQUEST) from error

		# Try to retrieve a similar OrderLine...
		# TODO ajout de la vérification de la limite de temps
		try:
			orderline = OrderLine.objects.get(order=order_pk, item=item_pk)
			serializer = OrderLineSerializer(orderline, data={ 'quantity': quantity }, partial=True)

			# Delete empty OrderLines
			if quantity <= 0:
				orderline.delete()
				return Response(serializer.initial_data, status=status.HTTP_205_RESET_CONTENT)

		except OrderLine.DoesNotExist as error:
			# ...or create a new one
			if quantity > 0:
				serializer = self.get_serializer(data={
					'order': order_pk,
					'item': item_pk,
					'quantity': quantity,
				})
			# If no quantity, then no OrderLine
			else:
				return Response({}, status=status.HTTP_204_NO_CONTENT)

		# Validate and create OrderLineSerializer
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
	"""

# ============================================
# 	Field & ItemField
# ============================================

class FieldViewSet(ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = Field.objects.all()
	serializer_class = FieldSerializer
	permission_classes = (IsAdminOrReadOnly,)

	def get_sub_urls_filters(self, queryset) -> dict:
		"""
		Override of core.viewsets.ModelViewSet for owner-user correspondance
		"""
		filters = super().get_sub_urls_filters(queryset)
		# Change item__pk for items__pk because of many-to-many relation
		if 'item__pk' in filters:
			filters['items__pk'] = filters.pop('item__pk')
		return filters


class ItemFieldViewSet(ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = ItemField.objects.all()
	serializer_class = ItemFieldSerializer
	permission_classes = (IsManagerOrReadOnly,)

# ============================================
# 	OrderLineItem & OrderLineField
# ============================================

class OrderLineItemViewSet(ModelViewSet):
	queryset = OrderLineItem.objects.all()
	serializer_class = OrderLineItemSerializer
	permission_classes = (IsOrderOwnerReadOnlyOrAdmin,)

class OrderLineFieldViewSet(ModelViewSet):
	"""
	Defines the view which display the items of an orderline
	"""
	queryset = OrderLineField.objects.all()
	serializer_class = OrderLineFieldSerializer
	permission_classes = (IsOrderOwnerReadUpdateOrAdmin,)

	def partial_update(self, request, *args, **kwargs):
		kwargs['partial'] = True
		return self.update(request, *args, **kwargs)

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		# Check if field is editable
		if instance.isEditable() == True:
			serializer = OrderLineFieldSerializer(instance, data={'value': request.data['value']}, partial=True)
			serializer.is_valid(raise_exception=True)
			serializer.save()
		else:
			serializer = OrderLineFieldSerializer(instance)
		return Response(serializer.data)


# ============================================
# 	Ticket
# ============================================

@api_view(['GET'])
@authentication_classes([OAuthAuthentication])
@permission_classes([IsOrderOwnerOrAdmin])
def generate_pdf(request, pk: int, **kwargs):
	# Get order
	order = Order.objects.all().prefetch_related(
					'orderlines', 'orderlines__orderlineitems', 'orderlines__item',
					'orderlines__orderlineitems__orderlinefields',
					'orderlines__orderlineitems__orderlinefields__field'
				).get(pk=pk)

	if order.status not in OrderStatus.VALIDATED_LIST.value:
		raise OrderValidationException(
			"La commande n'est pas valide", 'unvalid_order_tickets',
			details=f"Status: {order.get_status_display()}",
			status=status.HTTP_400_BAD_REQUEST)


	# Process tickets
	tickets = list()
	for orderline in order.orderlines.all():
		for orderlineitem in orderline.orderlineitems.all():
			# Process QRCode
			# TODO Move to helpers
			qr_buffer = BytesIO()
			code = data_to_qrcode(orderlineitem.id)
			code.save(qr_buffer)
			qr_code = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")

			# Add Nom et Prénom to orderline
			first_name = last_name = None
			for orderlinefield in orderlineitem.orderlinefields.all():
				if orderlinefield.field.name == 'Nom':
					first_name = orderlinefield.value
				elif orderlinefield.field.name == 'Prénom':
					last_name = orderlinefield.value
				
			if first_name is None:
				first_name = order.owner.first_name
			if last_name is None:
				last_name = order.owner.last_name

			# Add a ticket with this data
			tickets.append({
				'nom': first_name,
				'prenom': last_name,
				'qr_code': qr_code,
				'item': orderline.item,
				'uuid': orderlineitem.id,
			})
	data = {
		'tickets': tickets,
		'order': order,
	}

	# Render template
	template = 'pdf/template_order.html'
	if request.GET.get('type', 'pdf') == 'html':
		response = render(request, template, data)
	else:
		pdf = render_to_pdf(template, data)
		response = HttpResponse(pdf, content_type='application/pdf')
		if request.GET.get('download', 'false') != 'false':
			response['Content-Disposition'] = f'attachment;filename="commande_{order.sale.name}_{order.pk}.pdf"'
			
	return response
