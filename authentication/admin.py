from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from authentication.forms import UserCreationForm, UserChangeForm
from authentication.models import User,UserType


class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('is_admin', 'usertype')
	list_filter = ('is_admin',)
	fieldsets = (
		(None, {'fields': ('first_name', 'password', 'usertype')}),
		('Permissions', {'fields': ('is_admin',)}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide'),
			'fields': ('password1', 'password2', 'usertype')}
		 ),
	)
	search_fields = ('email',)
	ordering = ('last_name',)
	filter_horizontal = ()


# Register Models
admin.site.register(User, UserAdmin)
admin.site.register(UserType)

admin.site.unregister(Group)
