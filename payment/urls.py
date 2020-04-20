from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import PaymentView

urlpatterns = [
    path('orders/<int:pk>/pay',    PaymentView.pay,           name='order-pay'),
    path('orders/<int:pk>/status', PaymentView.update_status, name='order-status'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
