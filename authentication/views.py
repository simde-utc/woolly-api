from authentication.serializers import WoollyUserSerializer, WoollyUserTypeSerializer
from authentication.models import WoollyUserType, WoollyUser
from sales.models import AssociationMember
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework_json_api.views import RelationshipView
from django.http import HttpResponse,JsonResponse
from django.core.exceptions import ObjectDoesNotExist

class WoollyUserViewSet(viewsets.ModelViewSet):
    """support Post request to create a new WoollyUser"""
    queryset = WoollyUser.objects.all()
    serializer_class = WoollyUserSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        print("alaric5")
        serializer.save(
            type_id=self.kwargs['woollyusertype_pk']
        )

    def get_queryset(self):
        queryset = self.queryset.filter(login=self.request.user.login)

        if 'woollyuser_pk' in self.kwargs:
            association_pk = self.kwargs['woollyuser_pk']
            queryset = queryset.filter(user__pk=association_pk)

        return queryset

class WoollyUserTypeViewSet(viewsets.ModelViewSet):
    queryset = WoollyUserType.objects.all()
    serializer_class = WoollyUserTypeSerializer

    def get_queryset(self):
        print("alaric6")
        queryset = self.queryset.filter(users=self.request.user)

        if 'itemspec_pk' in self.kwargs:
            itemspec_pk = self.kwargs['itemspec_pk']
            queryset = WoollyUserType.objects.all().filter(itemspecifications__pk=itemspec_pk)

        if 'user_pk' in self.kwargs:
            user_pk = self.kwargs['user_pk']
            queryset = WoollyUserType.objects.all().filter(users__pk=user_pk)

        return queryset


class WoollyUserRelationshipView(RelationshipView):
    queryset = WoollyUser.objects

def userInfos(request):
    userId = request.session['_auth_user_id']
    try:
        queryset = WoollyUser.objects.get(id=userId)
        login = queryset.login
        lastName = queryset.last_name
        firstName = queryset.first_name
        response = {"userId":userId,"login":login,"lastName":lastName,"firstName":firstName}
    except WoollyUser.DoesNotExist:
        response =  {"userId":None,"login":None,"lastName":None,"firstName":None}
    return JsonResponse(response)