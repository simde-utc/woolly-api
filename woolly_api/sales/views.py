from rest_framework import viewsets
from rest_framework import permissions

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import permissions

from rest_framework_json_api.views import RelationshipView

from .models import Item, ItemSpecifications, Association, Sale, Order, OrderLine
from .serializers import ItemSerializer, ItemSpecificationsSerializer, AssociationSerializer
from .serializers import OrderSerializer, OrderLineSerializer, SaleSerializer
from authentication.models import WoollyUserType
from authentication.serializers import WoollyUserTypeSerializer
from .permissions import IsOwnerOrReadOnly
import pdb

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'assos': reverse('association-list', request=request, format=format),
        'sales': reverse('sale-list', request=request, format=format),
        'items': reverse('item-list', request=request, format=format),
        'specs': reverse('itemSpecification-list', request=request, format=format),
        'woollyusertypes': reverse('usertype-list', request=request, format=format),
        'orders': reverse('order-list', request=request, format=format),
        'orderlines': reverse('orderline-list', request=request, format=format),
    })


class AssociationViewSet(viewsets.ModelViewSet):
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)


    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )

    def get_queryset(self):
        queryset = self.queryset

        if 'woollyuser_pk' in self.kwargs:
            association_pk = self.kwargs['woollyuser_pk']
            queryset = queryset.filter(user__pk=association_pk)

        return queryset


class OrderLineViewSet(viewsets.ModelViewSet):

    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            order_id=self.kwargs['order_pk']
        )

    def get_queryset(self):
        queryset = self.queryset

        if 'order_pk' in self.kwargs:
            order_pk = self.kwargs['order_pk']
            queryset = queryset.filter(order__pk=order_pk)

        return queryset


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            association_id=self.kwargs['association_pk']
        )

    def get_queryset(self):
        queryset = self.queryset

        # if this viewset is accessed via the 'association-detail' route,
        # it wll have been passed the `association_pk` kwarg and the queryset
        # needs to be filtered accordingly; if it was accessed via the
        # unnested '/portes' route, the queryset should include all Portes
        if 'association_pk' in self.kwargs:
            association_pk = self.kwargs['association_pk']
            queryset = queryset.filter(association__pk=association_pk)

        return queryset


class ItemSpecificationsViewSet(viewsets.ModelViewSet):
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
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            sale_id=self.kwargs['sale_pk']
        )

    def get_queryset(self):
        queryset = self.queryset

        if 'sale_pk' in self.kwargs:
            sale_pk = self.kwargs['sale_pk']
            queryset = queryset.filter(sale__pk=sale_pk)

        # if 'orderline_pk' in self.kwargs:
        #    orderline_pk = self.kwargs['orderline_pk']
        #   queryset = queryset.filter(order_item_line__pk=orderline_pk)

        return queryset


class OrderLineItemViewSet(viewsets.ModelViewSet):
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
            queryset = queryset.filter(order_item_line__pk=orderline_pk)

        return queryset


class OrderRelationshipView(RelationshipView):
    queryset = Order.objects


class OrderLineRelationshipView(RelationshipView):
    queryset = OrderLine.objects


class ItemRelationshipView(RelationshipView):
    queryset = Item.objects


class SaleRelationshipView(RelationshipView):
    queryset = Sale.objects


class ItemSpecificationsRelationshipView(RelationshipView):
    queryset = ItemSpecifications.objects


class AssociationRelationshipView(RelationshipView):
    queryset = Association.objects
