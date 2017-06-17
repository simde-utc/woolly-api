from rest_framework import viewsets
from rest_framework import permissions

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

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'assos': reverse('association-list', request=request, format=format),
        'sales': reverse('sale-list', request=request, format=format),
        'items': reverse('item-list', request=request, format=format),
        'itemSpecifications': reverse('itemSpecification-list', request=request, format=format),
        'woollyusertypes': reverse('usertype-list', request=request, format=format),
        'orders': reverse('order-list', request=request, format=format),
        'orderlines': reverse('orderline-list', request=request, format=format),
        'paymentmethods': reverse('paymentmethod-list', request=request, format=format),
        'associationmembers': reverse('associationmember-list', request=request, format=format),
    })


class AssociationViewSet(viewsets.ModelViewSet):
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


class AssociationMemberViewSet(viewsets.ModelViewSet):
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

    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            order_id=self.kwargs['order_pk']
        )

    def get_queryset(self):
        queryset = self.queryset.filter(order__owner=self.request.user)

        if 'order_pk' in self.kwargs:
            order_pk = self.kwargs['order_pk']
            queryset = OrderLine.objects.all().filter(order__pk=order_pk)

        return queryset


class SaleViewSet(viewsets.ModelViewSet):
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
    queryset = Order.objects


class OrderLineRelationshipView(RelationshipView):
    queryset = OrderLine.objects


class ItemRelationshipView(RelationshipView):
    queryset = Item.objects


class SaleRelationshipView(RelationshipView):
    queryset = Sale.objects


class AssociationMemberRelationshipView(RelationshipView):
    queryset = AssociationMember.objects


class ItemSpecificationsRelationshipView(RelationshipView):
    queryset = ItemSpecifications.objects


class AssociationRelationshipView(RelationshipView):
    queryset = Association.objects


class PaymentMethodRelationshipView(RelationshipView):
    queryset = PaymentMethod.objects
