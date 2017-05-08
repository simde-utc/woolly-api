# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import WoollyUser
from core.forms import WoollyUserCreationForm, WoollyUserChangeForm

# Register your models here.

class UserAdmin(BaseUserAdmin):
	form = WoollyUserChangeForm
	add_form = WoollyUserCreationForm

	list_display = ('login', 'is_admin')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields' : ('login', 'password')}),
		('Permissions', {'fields': ('is_admin',)}),
	)
	
	add_fieldsets = (
		(None, {
			'classes' : ('wide'),
			'fields': ('login', 'password1', 'password2')}
		),
	)
	search_fields = ('login',)
	ordering = ('login',)
	filter_horizontal = ()
	
admin.site.register(WoollyUser, UserAdmin)

admin.site.unregister(Group)
