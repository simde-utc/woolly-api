from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from authentication.oauth import OAuthAuthentication
from core.utils import render_to_pdf, base64_qrcode
from core.viewsets import ModelViewSet, APIModelViewSet
from core.permissions import CanOnlyReadOrUpdate, IsAdmin, IsAdminOrReadOnly
from sales.exceptions import OrderValidationException
from sales.permissions import (
    IsOwnerOrManager, IsOwnerOrManagerReadOnly, IsManagerOrReadOnly
)
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


# --------------------------------------------
#   Associations
# --------------------------------------------

class AssociationViewSet(APIModelViewSet):
    """
    Defines the behavior of the association view
    """
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_sub_urls_filters(self, queryset) -> dict:
        """
        Override of core.viewsets.ModelViewSet for owner-user correspondance
        """
        filters = super().get_sub_urls_filters(queryset)
        # Remove user__pk because it is not used for model lookup
        filters.pop('user__pk', None)
        return filters


class SaleViewSet(ModelViewSet):
    """
    Defines the behavior of the sale view
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsManagerOrReadOnly]

    # TODO Check for association in data or url for create/update

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter active sales
        if not self.query_params_is_true('include_inactive'):
            queryset = queryset.filter(is_active=True)

        # Filter public sales
        if 'pk' not in self.kwargs:
            queryset = queryset.filter(is_public=True)

        return queryset


# --------------------------------------------
#   Items
# --------------------------------------------

class ItemGroupViewSet(ModelViewSet):
    """
    Defines the behavior of the itemGroup interactions
    """
    queryset = ItemGroup.objects.all()
    serializer_class = ItemGroupSerializer
    permission_classes = [IsManagerOrReadOnly]


class ItemViewSet(ModelViewSet):
    """
    Defines the behavior of the item interactions
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Remove inactive sales by default
        if not self.query_params_is_true('include_inactive'):
            queryset = queryset.filter(is_active=True)

        return queryset


# --------------------------------------------
#   Orders
# --------------------------------------------

class OrderViewSet(ModelViewSet):
    """
    Defines the behavior of the Order CRUD

    TODO: update status if not stable
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrManagerReadOnly]

    def get_sub_urls_filters(self, queryset) -> dict:
        """
        Simply map user__pk to owner__pk in urls filters
        """
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
        sale_pk = self.get_kwarg('sale_pk', 'sale')
        try:
            # TODO ajout de la limite de temps
            order = self.get_queryset() \
                .filter(status__in=OrderStatus.BUYABLE_STATUS_LIST.value) \
                .get(sale=sale_pk, owner=request.user.id)

            serializer = self.get_serializer(instance=order)
            status_code = status.HTTP_200_OK
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
            status_code = status.HTTP_201_CREATED

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status_code, headers=headers)

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
        # TODO A tester
        # elif order.status == OrderStatus.ONGOING.value:
        #   order.delete()
        #   return Response(None, status=status.HTTP_204_NO_CONTENT)
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
    permission_classes = [IsOwnerOrManagerReadOnly]

    def get_sub_urls_filters(self, queryset) -> dict:
        """
        Simply map user__pk to owner__pk in urls filters
        """
        filters = super().get_sub_urls_filters(queryset)
        if 'sale__pk' in filters:
            filters['order__sale__pk'] = filters.pop('sale__pk')
        return filters

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
        order_pk = self.get_kwarg('order_pk', 'order')
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
                status_code=status.HTTP_400_BAD_REQUEST
            ) from error

        # Try to retrieve a similar OrderLine...
        # TODO ajout de la vérification de la limite de temps
        try:
            orderline = OrderLine.objects.get(order=order_pk, item=item_pk)
            serializer = OrderLineSerializer(orderline, data={ 'quantity': quantity }, partial=True)

            # Delete empty OrderLines
            if quantity <= 0:
                orderline.delete()
                return Response(serializer.initial_data, status=status.HTTP_205_RESET_CONTENT)

        except OrderLine.DoesNotExist:
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


class OrderLineItemViewSet(ModelViewSet):
    queryset = OrderLineItem.objects.all()
    serializer_class = OrderLineItemSerializer
    permission_classes = [IsAdminOrReadOnly & IsOwnerOrManager]


# --------------------------------------------
#   Fields
# --------------------------------------------

class FieldViewSet(ModelViewSet):
    """
    Defines the view which display the items of an orderline
    """
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_sub_urls_filters(self, queryset) -> dict:
        """
        Change item__pk for items__pk because of many-to-many relation
        """
        filters = super().get_sub_urls_filters(queryset)
        if 'item__pk' in filters:
            filters['items__pk'] = filters.pop('item__pk')
        return filters


class ItemFieldViewSet(ModelViewSet):
    """
    Defines the view which display the items of an orderline
    """
    queryset = ItemField.objects.all()
    serializer_class = ItemFieldSerializer
    permission_classes = [IsManagerOrReadOnly]


class OrderLineFieldViewSet(ModelViewSet):
    """
    Defines the view which display the items of an orderline
    """
    queryset = OrderLineField.objects.all()
    serializer_class = OrderLineFieldSerializer
    permission_classes = [IsAdmin | (CanOnlyReadOrUpdate & IsOwnerOrManager)]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Check if field is editable
        if instance.is_editable():
            serializer = OrderLineFieldSerializer(instance, data={'value': request.data['value']}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = OrderLineFieldSerializer(instance)
        return Response(serializer.data)


# --------------------------------------------
#   Tickets
# --------------------------------------------

@api_view(['GET'])
@authentication_classes([OAuthAuthentication])
@permission_classes([IsOwnerOrManagerReadOnly])
def generate_tickets(request, pk: int, **kwargs):
    # Get order
    order = Order.objects.all().prefetch_related(
        'orderlines', 'orderlines__orderlineitems', 'orderlines__item',
        'orderlines__orderlineitems__orderlinefields',
        'orderlines__orderlineitems__orderlinefields__field'
    ).get(pk=pk)

    # Check order is valid
    if order.status not in OrderStatus.VALIDATED_LIST.value:
        raise OrderValidationException(
            "La commande n'est pas valide", 'unvalid_order_tickets',
            details=f"Status: {order.get_status_display()}",
            status=status.HTTP_400_BAD_REQUEST)

    # Process tickets
    tickets = []
    for orderline in order.orderlines.all():
        for orderlineitem in orderline.orderlineitems.all():
            # Process QRCode
            orderline_code = str(orderlineitem.id).replace('-', '')
            qr_code = base64_qrcode(orderline_code)

            # TODO Add more flexibility
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

    # Render template
    template = 'pdf/template_order.html'
    data = {
        'tickets': tickets,
        'order': order,
    }
    if request.GET.get('type', 'pdf') == 'html':
        return render(request, template, data)
    else:
        pdf = render_to_pdf(template, data)
        response = HttpResponse(pdf, content_type='application/pdf')

        # Add download header by default
        if request.GET.get('download', 'false') != 'false':
            filename = f"Woolly_{order.sale.name}_{order.pk}.pdf"
            response['Content-Disposition'] = f'attachment;filename="{filename}"'

        return response
