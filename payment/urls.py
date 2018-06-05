from django.conf.urls import url, include
from woolly_api.settings import VIEWSET
from .views import *

urlpatterns = [
	url(r'^orders/(?P<pk>[0-9]+)/pay$', pay, name = 'order-pay'),
	url(r'^orders/(?P<pk>[0-9]+)/pay_callback$', pay_callback, name = 'pay-callback'),
]





"""
paymentmethod_list   = PaymentMethodViewSet.as_view(VIEWSET['list'])
paymentmethod_detail = PaymentMethodViewSet.as_view(VIEWSET['detail'])
	# ============================================
	# 	Payment Methods : A VIRER
	# ============================================
	url(r'^paymentmethods$',
		view = paymentmethod_list, name = 'paymentmethod-list'),
	url(r'^paymentmethods/(?P<pk>[0-9]+)$',
		view = paymentmethod_detail, name = 'paymentmethod-detail'),
	url(r'^paymentmethods/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
		view = PaymentMethodRelationshipView.as_view(), name = 'paymentmethod-relationships'),

	url(r'^sales/(?P<sale_pk>[0-9]+)/paymentmethods$',
		view = paymentmethod_list, name = 'paymentmethod-list'),
	url(r'^sales/(?P<sale_pk>[0-9]+)/paymentmethods/(?P<pk>[0-9]+)$',
		view = paymentmethod_detail, name = 'paymentmethod-detail'),
	url(r'^paymentmethods/(?P<payment_pk>[0-9]+)/sales$',
		view = sale_list, name = 'sale-payment-list'),
	url(r'^paymentmethods/(?P<payment_pk>[0-9]+)/sales/(?P<pk>[0-9]+)$',
		view = sale_detail, name = 'sale-payment-detail'),

"""