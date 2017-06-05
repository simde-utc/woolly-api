from rest_framework.generics import CreateAPIView
from authentication.serializers import WoollyUserSerializer, WoollyUserTypeSerializer
from authentication.models import WoollyUserType
from rest_framework.permissions import AllowAny
from rest_framework import viewsets


class CreateWoollyUserView(CreateAPIView):
    """support Post request to create a new WoollyUser"""
    serializer_class = WoollyUserSerializer
    permission_classes = (AllowAny,)


class WoollyUserTypeViewSet(viewsets.ModelViewSet):
    queryset = WoollyUserType.objects.all()
    serializer_class = WoollyUserTypeSerializer

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
