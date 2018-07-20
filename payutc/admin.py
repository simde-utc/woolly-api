from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from authentication.models import User
from authentication.forms import UserCreationForm, UserChangeForm

from authentication.models import UserType


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('login', 'is_admin', 'usertype')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('login', 'password', 'usertype')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('login', 'password1', 'password2', 'usertype')}
         ),
    )
    search_fields = ('login',)
    ordering = ('login',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(UserType)

admin.site.unregister(Group)
