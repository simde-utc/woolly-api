from rest_framework import generics
from core.serializers.orderLine import OrderLineSerializer
from core.serializers.order import OrderSerializer
from core.models.orderLine import OrderLine
from rest_framework import permissions


class CreateOrderLineView(generics.ListCreateAPIView):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save(
            user=self.request.user,
            order=self.kwargs['pk'])

class OrderLineDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer

# Test : Implement a way to return only order items according to the order id
# Doesn't work yet
class OrderLineView(generics.ListAPIView):
    queryset = OrderLine.objects.raw("SELECT * FROM core_orderline")
    serializer_class = OrderLineSerializer
