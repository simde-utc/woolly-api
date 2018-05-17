from django.contrib import admin
from .models import Item, ItemGroup, Association, Sale, Order, OrderLine, PaymentMethod, AssociationMember, \
	OrderLineField, ItemField, Field
# Register your models here.
admin.site.register(Item)
admin.site.register(ItemGroup)
admin.site.register(Association)
admin.site.register(Sale)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(PaymentMethod)
admin.site.register(AssociationMember)
admin.site.register(OrderLineField)
admin.site.register(ItemField)
admin.site.register(Field)
