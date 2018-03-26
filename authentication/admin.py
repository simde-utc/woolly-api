from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from authentication.models import WoollyUser
from authentication.forms import WoollyUserCreationForm, WoollyUserChangeForm

from authentication.models import WoollyUserType


class UserAdmin(BaseUserAdmin):
    form = WoollyUserChangeForm
    add_form = WoollyUserCreationForm

    list_display = ('login', 'is_admin', 'woollyusertype')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('login', 'password', 'woollyusertype')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('login', 'password1', 'password2', 'woollyusertype')}
         ),
    )
    search_fields = ('login',)
    ordering = ('login',)
    filter_horizontal = ()

admin.site.register(WoollyUser, UserAdmin)
admin.site.register(WoollyUserType)

admin.site.unregister(Group)
