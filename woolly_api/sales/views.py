from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rest_framework_json_api.views import RelationshipView

from .models import Item, ItemSpecifications, Association, Sale, WoollyUserType
from .serializers import ItemSerializer, WoollyUserTypeSerializer, ItemSpecificationsSerializer2, SaleSerializer, AssociationSerializer

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'assos': reverse('association-list', request=request, format=format),
        'sales': reverse('sale-list', request=request, format=format),
        'items': reverse('item-list', request=request, format=format),
    })


class AssociationViewSet(viewsets.ModelViewSet):
    queryset = Association.objects.all()
    serializer_class = AssociationSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

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
    serializer_class = ItemSpecificationsSerializer2

    def perform_create(self, serializer):
        serializer.save(
            item_id=self.kwargs['item_pk']
        )

    def get_queryset(self):
        queryset = self.queryset

        # if this viewset is accessed via the 'association-detail' route,
        # it wll have been passed the `association_pk` kwarg and the queryset
        # needs to be filtered accordingly; if it was accessed via the
        # unnested '/portes' route, the queryset should include all Portes
        if 'item_pk' in self.kwargs:
            item_pk = self.kwargs['item_pk']
            queryset = queryset.filter(item__pk=item_pk)

        return queryset

"""
class ItemSpecificationsList(generics.ListCreateAPIView):
    queryset = ItemSpecifications.objects.all()
    serializer_class = ItemSpecificationsSerializer2
    lookup_url_kwarg = 'item_id'

    def perform_create(self, serializer):
        serializer.save(
            name=self.kwargs['type_id'],
            item_id=self.kwargs['item_id'])

    def get_queryset(self):
        item = self.kwargs['item_id']
        return ItemSpecifications.objects.filter(item_id=item)
"""


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        serializer.save(
            sale_id=self.kwargs['sale_pk']
        )

    def get_queryset(self):
        queryset = self.queryset

        # if this viewset is accessed via the 'association-detail' route,
        # it wll have been passed the `association_pk` kwarg and the queryset
        # needs to be filtered accordingly; if it was accessed via the
        # unnested '/portes' route, the queryset should include all Portes
        if 'sale_pk' in self.kwargs:
            sale_pk = self.kwargs['sale_pk']
            queryset = queryset.filter(sale__pk=sale_pk)

        return queryset


class WoollyUserTypeViewSet(viewsets.ModelViewSet):
    queryset = WoollyUserType.objects.all()
    serializer_class = WoollyUserTypeSerializer
    """
    def perform_create(self, serializer):
        serializer.save(
            sale_id=self.kwargs['sale_pk']
        )
    """

    def get_queryset(self):
        queryset = self.queryset

        # if this viewset is accessed via the 'association-detail' route,
        # it wll have been passed the `association_pk` kwarg and the queryset
        # needs to be filtered accordingly; if it was accessed via the
        # unnested '/portes' route, the queryset should include all Portes
        if 'itemspec_pk' in self.kwargs:
            itemspec_pk = self.kwargs['itemspec_pk']
            queryset = queryset.filter(specs__pk=itemspec_pk)

        return queryset


class ItemRelationshipView(RelationshipView):
    queryset = Item.objects


class SaleRelationshipView(RelationshipView):
    queryset = Sale.objects


class ItemSpecificationsRelationshipView(RelationshipView):
    queryset = ItemSpecifications.objects


class WoollyUserTypeRelationshipView(RelationshipView):
    queryset = WoollyUserType.objects


class AssociationRelationshipView(RelationshipView):
    queryset = Association.objects
