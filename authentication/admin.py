from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserType

class UserAdmin(BaseUserAdmin):

	list_display = ('email', 'first_name', 'last_name', 'is_admin')
	list_filter = ('is_admin',)
	list_editable = tuple()

	fieldsets = (
		(None,          { 'fields': ('email', 'first_name', 'last_name') }),
		('Permissions', { 'fields': ('is_admin',) }),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide'),
			'fields': ('email', 'first_name', 'last_name')
		}),
	)
	search_fields = ('email', 'first_name', 'last_name')
	ordering = ('last_name', 'first_name')
	filter_horizontal = ()


# Register Models
admin.site.register(User, UserAdmin)
admin.site.register(UserType)

admin.site.unregister(Group)
