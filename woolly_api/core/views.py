# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework import generics, permissions
from .serializers import OrderSerializer, ItemSerializer
from .permissions import IsOwner
from .models import Order, Item
from django.contrib.auth import get_user_model
from rest_framework import permissions

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

class CreateItemView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()

class ItemDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
