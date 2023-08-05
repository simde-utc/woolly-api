from django.views import View
from rest_framework_json_api import views
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from core.helpers import errorResponse
from core.permissions import *
from .serializers import *
from .permissions import *
from .models import OrderStatus

from authentication.auth import JWTAuthentication
from core.utils import render_to_pdf, data_to_qrcode
from django.shortcuts import render
from io import BytesIO
import base64

# ============================================
# 	Association
# ============================================

class AssociationViewSet(views.ModelViewSet):
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
	permission_classes = (IsManagerOrReadOnly,)

	def get_queryset(self):
		queryset = Sale.objects.all()
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
			association_pk = self.kwargs['association_pk']
			queryset = queryset.filter(association__pk=association_pk)

		return queryset

class SaleRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the sales related links
	"""
	queryset = Sale.objects


# ============================================
# 	Item
# ============================================

class ItemGroupViewSet(views.ModelViewSet):
	"""
	Defines the behavior of the itemGroup interactions
	"""
	queryset = ItemGroup.objects.all()
	serializer_class = ItemGroupSerializer
	permission_classes = (IsManagerOrReadOnly,)

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

		try:
			quantity = int(request.data.get('quantity', 0))
			assert quantity >= 0
		except (ValueError, AssertionError) as error:
			msg = "La quantité d'article à acheter doit être positive ou nulle."
			return errorResponse(msg, [msg], status.HTTP_400_BAD_REQUEST)

		# Try to retrieve a similar OrderLine...
		try:
			orderline = OrderLine.objects.get(order=request.data['order']['id'], item=request.data['item']['id'])
			# TODO ajout de la vérification de la limite de temps
			serializer = OrderLineSerializer(orderline, data={'quantity': quantity}, partial=True)

			# Delete empty OrderLines
			if quantity <= 0:
				orderline.delete()
				return Response(serializer.initial_data, status=status.HTTP_205_RESET_CONTENT)
		# ...or create a new one
		except OrderLine.DoesNotExist as err:
			if quantity > 0:
				# Configure Order
				serializer = self.get_serializer(data={
					'order': request.data['order'],
					'item': request.data['item'],
					'quantity': quantity,
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

class OrderLineRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLine.objects


# ============================================
# 	Field & ItemField
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
	permission_classes = (IsManagerOrReadOnly,)

class ItemFieldRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = ItemField.objects

# ============================================
# 	OrderLineItem & OrderLineField
# ============================================

class OrderLineItemViewSet(views.ModelViewSet):
	queryset = OrderLineItem.objects.all()
	serializer_class = OrderLineItemSerializer
	permission_classes = (IsOrderOwnerReadOnlyOrAdmin,)

class OrderLineItemRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLineItem.objects


class OrderLineFieldViewSet(views.ModelViewSet):
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

class OrderLineFieldRelationshipView(views.RelationshipView):
	"""
	Required by JSON API to display the orderlines related links
	"""
	queryset = OrderLineField.objects


# ============================================
# 	Billet
# ============================================
class GeneratePdf(View):

	def get(self, request, *args, **kwargs):
		# Authenticate by forcing JWT from ?code=...
		request.META['HTTP_AUTHORIZATION'] = "Bearer " + request.GET.get('code', '')
		jwtAuth = JWTAuthentication()
		authUser = jwtAuth.authenticate(request)

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
			print(order)
		except Order.DoesNotExist as e:
			return errorResponse('La commande est introuvable', [], httpStatus = status.HTTP_404_NOT_FOUND)
		except Exception as e:
    			print (traceback.format_exc())
		# Process tickets
		tickets = list()
		for orderline in order.orderlines.all():
			for orderlineitem in orderline.orderlineitems.all():
				# Process QRCode
				qr_buffer = BytesIO()
				code = data_to_qrcode(orderlineitem.id)
				code.save(qr_buffer, format="PNG")
				qr_code = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")

				# Add Nom et Prénom to orderline
				first_name = None
				last_name = None
				for orderlinefield in orderlineitem.orderlinefields.all():
					if orderlinefield.field.name == 'Nom':
						first_name = orderlinefield.value
						continue
					if orderlinefield.field.name == 'Prénom':
						last_name = orderlinefield.value
				
				if first_name == None:
					first_name = order.owner.first_name
				if last_name == None:
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
			'order': order
		}
		print(data)
		# Render template
		template = 'pdf/template_order.html'
		if order.sale.pk == 20:
			template = 'pdf/billet_lightup.html'

		if request.GET.get('type', 'pdf') == 'html':
			response = render(request, template, data)
		else:
			pdf = render_to_pdf(template, data)
			response = HttpResponse(pdf, content_type='application/pdf')
			if request.GET.get('action', 'download') != 'view':
				response['Content-Disposition'] = 'attachment;filename="commande_' + order.sale.name + '_' + order_pk + '.pdf"'
		return response
