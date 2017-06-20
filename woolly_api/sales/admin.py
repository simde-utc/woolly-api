from django.contrib import admin
from .models import Item, ItemSpecifications, Association, Sale, Order, OrderLine, PaymentMethod, AssociationMember
# Register your models here.
admin.site.register(Item)
admin.site.register(ItemSpecifications)
admin.site.register(Association)
admin.site.register(Sale)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(PaymentMethod)
admin.site.register(AssociationMember)
