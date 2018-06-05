from django.conf.urls import url, include
from woolly_api.settings import VIEWSET
from .views import *

urlpatterns = [
	url(r'^orders/(?P<pk>[0-9]+)/pay$', pay, name = 'order-pay'),
	url(r'^orders/(?P<pk>[0-9]+)/pay_callback$', pay_callback, name = 'pay-callback'),
]