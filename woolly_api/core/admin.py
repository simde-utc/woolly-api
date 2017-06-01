# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from core.models import Item, ItemGroup, ItemSpecifications, Order, OrderLine


admin.site.register(Item)
admin.site.register(ItemGroup)
admin.site.register(ItemSpecifications)
admin.site.register(Order)
admin.site.register(OrderLine)

