from rest_framework.generics import CreateAPIView
from authentication.serializers import WoollyUserSerializer
from rest_framework.permissions import AllowAny


class CreateWoollyUserView(CreateAPIView):
	"""support Post request to create a new WoollyUser"""
	serializer_class = WoollyUserSerializer
	permission_classes = (AllowAny,)

