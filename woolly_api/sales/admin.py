from django.contrib import admin
from .models import Item, ItemSpecifications, Association, Sale, WoollyUserType
# Register your models here.
admin.site.register(Item)
# admin.site.register(ItemGroup)
admin.site.register(ItemSpecifications)
admin.site.register(Association)
admin.site.register(Sale)
admin.site.register(WoollyUserType)