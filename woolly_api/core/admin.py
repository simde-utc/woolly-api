# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import WoollyUser
from core.forms import WoollyUserCreationForm, WoollyUserChangeForm

from core.models import WoollyUserType, Item, ItemGroup, ItemSpecifications, Order, OrderLine


class UserAdmin(BaseUserAdmin):
	form = WoollyUserChangeForm
	add_form = WoollyUserCreationForm

	list_display = ('login', 'is_admin','type')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields' : ('login', 'password','type')}),
		('Permissions', {'fields': ('is_admin',)}),
	)

	add_fieldsets = (
		(None, {
			'classes' : ('wide'),
			'fields': ('login', 'password1', 'password2', 'type')}
		),
	)
	search_fields = ('login',)
	ordering = ('login',)
	filter_horizontal = ()

admin.site.register(WoollyUser, UserAdmin)
admin.site.register(WoollyUserType)
admin.site.register(Item)
admin.site.register(ItemGroup)
admin.site.register(ItemSpecifications)
admin.site.register(Order)
admin.site.register(OrderLine)

admin.site.unregister(Group)
