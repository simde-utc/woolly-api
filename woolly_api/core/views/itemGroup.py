from rest_framework import generics
from core.serializers.itemGroup import ItemGroupSerializer
from core.models.itemGroup import ItemGroup
from rest_framework import permissions


class CreateItemGroupView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = ItemGroup.objects.all()
    serializer_class = ItemGroupSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Save the post data when creating a new item"""
        serializer.save()

class ItemGroupDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ItemGroup.objects.all()
    serializer_class = ItemGroupSerializer
    permission_classes = (permissions.IsAuthenticated, )
