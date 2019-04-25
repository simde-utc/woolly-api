from django.views import View
from rest_framework_json_api import views
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import HttpResponse

from core.helpers import errorResponse
from core.permissions import *
from .serializers import *
from .permissions import *
from .models import OrderStatus

from authentication.auth import APIAuthentication
from core.utils import render_to_pdf, data_to_qrcode
from django.shortcuts import render
from io import BytesIO
import base64

# from core.views import ModelViewSet
ModelViewSet = viewsets.ModelViewSet

# ============================================
# 	Association
# ============================================

class AssociationViewSet(ModelViewSet):
	"""
	Defines the behavior of the association view
	"""
	queryset = Association.objects.all()
	serializer_class = AssociationSerializer
	permission_classes = (IsManagerOrReadOnly,)

	def get_queryset(self):
		queryset = self.queryset

		# user-association-list
		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(members__pk=user_pk)

		return queryset

class AssociationMemberViewSet(ModelViewSet):
	"""
	Defines the behavior link to the association member view
	"""
	queryset = AssociationMember.objects.all()
	serializer_class = AssociationMemberSerializer
	permission_classes = (IsManager,)

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

	def get_queryset(self):
		queryset = self.queryset
					# .filter(items__itemspecifications__user_type__name=self.request.user.usertype.name)
					# TODO filtrer par date ?

		queryset = queryset.filter(is_active=True, public=True)
		# TODO V2 : filtering
		# filters = ('active', )
		# filterQuery = self.request.query_params.get('filterQuery', None)
		# if filterQuery is not None:
			# queryset = queryset.filter()
			# pass

		# Association detail route
		if 'association_pk' in self.kwargs:
			queryset = queryset.filter(association__pk=self.kwargs['association_pk'])

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
		queryset = self.queryset.filter(is_active=True)

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
	Defines the behavior of the order CRUD
	"""
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	permission_classes = (IsOrderOwnerOrAdmin,)

	def get_queryset(self):
		user = self.request.user
		queryset = self.queryset

		# Anonymous users see nothing
		if not user.is_authenticated:
			return None

		# Admins see everything otherwise filter to see only those owned by the user
		# if not user.is_admin:
		# 	queryset = queryset.filter(owner=user)

		if 'user_pk' in self.kwargs:
			user_pk = self.kwargs['user_pk']
			queryset = queryset.filter(owner__pk=user_pk)

		return queryset

	def create(self, request):
		"""Find if user has a Buyable Order or create"""
		try:
			# TODO ajout de la limite de temps
			order = Order.objects \
				.filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
				.get(sale=request.data['sale']['id'], owner=request.user.id)

			serializer = OrderSerializer(order)
			httpStatus = status.HTTP_200_OK
		except Order.DoesNotExist as err:
			# Configure new Order
			serializer = OrderSerializer(data = {
				'sale': request.data['sale'],
				'owner': {
					'id': request.user.id,
					'type': 'users'
				},
				'orderlines': [],
				'status': OrderStatus.ONGOING.value
			})
			serializer.is_valid(raise_exception=True)
			self.perform_create(serializer)
			httpStatus = status.HTTP_201_CREATED

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=httpStatus, headers=headers)

	def destroy(self, request, *args, **kwargs):
		order = self.get_object()
		if order.status in OrderStatus.CANCELLABLE_LIST.value:
			# TODO Add time
			order.status = OrderStatus.CANCELLED.value
			order.save()
			return Response(None, status=status.HTTP_204_NO_CONTENT)
		else:
			msg = "La commande n'est pas annulable."
			return errorResponse(msg, [msg], status.HTTP_406_NOT_ACCEPTABLE)

class OrderLineViewSet(ModelViewSet):
	"""
	Defines the behavior of the Orderline view
	"""
	queryset = OrderLine.objects.all()
	serializer_class = OrderLineSerializer
	permission_classes = (IsOrderOwnerOrAdmin,)

	def get_queryset(self):
		user = self.request.user
		queryset = self.queryset

		# Anonymous users see nothing
		if not user.is_authenticated:
			return None

		# Admins see everything otherwise filter to see only those owned by the user
		# if not user.is_admin:
		# 	queryset = queryset.filter(order__owner=user)

		if 'order_pk' in self.kwargs:
			order_pk = self.kwargs['order_pk']
			queryset = OrderLine.objects.all().filter(order__pk=order_pk)

		return queryset

	def create(self, request, *args, **kwargs):
		# Retrieve Order...
		try:
			order = Order.objects.get(pk=request.data['order']['id'])
		# ...or fail
		except Order.DoesNotExist as err:
			msg = "Impossible de trouver la commande."
			return errorResponse(msg, [msg], status.HTTP_404_NOT_FOUND)

		# Check Order owner
		user = request.user
		if not (user.is_authenticated and user.is_admin or order.owner == user):
			msg = "Vous n'avez pas la permission d'effectuer cette action."
			return errorResponse(msg, [msg], status.HTTP_403_FORBIDDEN)

		# Check if Order is open
		if order.status != OrderStatus.ONGOING.value:
			msg = "La commande n'accepte plus de changement."
			return errorResponse(msg, [msg], status.HTTP_400_BAD_REQUEST)

		# Try to retrieve a similar OrderLine...
		try:
			orderline = OrderLine.objects.get(order=request.data['order']['id'], item=request.data['item']['id'])
			# TODO ajout de la vérification de la limite de temps
			serializer = OrderLineSerializer(orderline, data={'quantity': request.data['quantity']}, partial=True)

			# Delete empty OrderLines
			if request.data['quantity'] <= 0:
				orderline.delete()
				return Response(serializer.initial_data, status=status.HTTP_205_RESET_CONTENT)
		# ...or create a new one
		except OrderLine.DoesNotExist as err:
			if request.data['quantity'] > 0:
				# Configure Order
				serializer = self.get_serializer(data={
					'order': request.data['order'],
					'item': request.data['item'],
					'quantity': request.data['quantity'],
				})
			# If no quantity, then no OrderLine
			else:
				return Response(request.data, status=status.HTTP_204_NO_CONTENT)
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

	def get_queryset(self):
		queryset = self.queryset
		if 'orderlineitem_pk' in self.kwargs:
			orderlineitem_pk = self.kwargs['orderlineitem_pk']
			queryset = queryset.filter(orderlineitem__pk=orderlineitem_pk)

		return queryset

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop('partial', False)
		instance = self.get_object()
		if instance.isEditable() == True:
			serializer = OrderLineFieldSerializer(instance, data={'value': request.data['value']}, partial=True)
			serializer.is_valid(raise_exception=True)
			serializer.save()
		else:
			serializer = OrderLineFieldSerializer(instance)
		return Response(serializer.data)

# ============================================
# 	Billet
# ============================================

class GeneratePdf(View):

	def get(self, request, *args, **kwargs):
		# Authenticate
		authUser = APIAuthentication().authenticate(request)

		if authUser is None:
			return errorResponse("Valid Code Required", [], httpStatus = status.HTTP_401_UNAUTHORIZED)
		request.user = authUser[0]

		# Get order
		order_pk = self.kwargs.get('order_pk', None)
		try:
			order = Order.objects.all() \
						.filter(owner__pk=request.user.pk, status__in=OrderStatus.VALIDATED_LIST.value) \
						.prefetch_related('orderlines', 'orderlines__orderlineitems', 'orderlines__item',
							'orderlines__orderlineitems__orderlinefields', 'orderlines__orderlineitems__orderlinefields__field') \
						.get(pk=order_pk)
		except Order.DoesNotExist as e:
			return errorResponse('La commande est introuvable', [], httpStatus = status.HTTP_404_NOT_FOUND)

		# Process tickets
		tickets = list()
		for orderline in order.orderlines.all():
			for orderlineitem in orderline.orderlineitems.all():
				# Process QRCode
				qr_buffer = BytesIO()
				code = data_to_qrcode(orderlineitem.id)
				code.save(qr_buffer)
				qr_code = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")

				# Add Nom et Prénom to orderline
				for orderlinefield in orderlineitem.orderlinefields.all():
					if orderlinefield.field.name == 'Nom':
						first_name = orderlinefield.value
						continue
					if orderlinefield.field.name == 'Prénom':
						last_name = orderlinefield.value
				
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
			'order': order
		}

		# Render template
		template = 'pdf/template_order.html'
		if request.GET.get('type', 'pdf') == 'html':
			response = render(request, template, data)
		else:
			pdf = render_to_pdf(template, data)
			response = HttpResponse(pdf, content_type='application/pdf')
			if request.GET.get('action', 'download') != 'view':
				response['Content-Disposition'] = 'attachment;filename="commande_' + order.sale.name + '_' + order_pk + '.pdf"'
				
		return response
