from rest_framework import generics
from core.serializers.item import ItemSerializer
from core.models.item import Item
from rest_framework import permissions


class CreateItemView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Save the post data when creating a new item"""
        serializer.save()

class ItemDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
