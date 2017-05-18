from rest_framework import generics
from core.serializers import OrderSerializer
from core.models import Order
from rest_framework import permissions
from core.permissions import IsOwner


class CreateOrderView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save(user=self.request.user)


class OrderDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,IsOwner)
