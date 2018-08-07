from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserType
from .forms import UserCreationForm, UserChangeForm
from sales.admin import AssociationMemberInline

class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ('email', 'first_name', 'last_name', 'usertype', 'is_admin')
	list_filter = ('is_admin', 'usertype')
	list_editable = tuple()

	inlines = (AssociationMemberInline,)
	fieldsets = (
		(None, { 'fields': ('email', 'password', 'first_name', 'last_name', 'usertype') }),
		('Permissions', { 'fields': ('is_admin',) }),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide'),
			'fields': ('email', 'first_name', 'last_name', 'usertype', 'password1', 'password2')}
		 ),
	)
	search_fields = ('email', 'first_name', 'last_name')
	ordering = ('last_name', 'first_name')
	filter_horizontal = ()


# Register Models
admin.site.register(User, UserAdmin)
admin.site.register(UserType)

admin.site.unregister(Group)
