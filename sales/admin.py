from django.contrib import admin
from .models import *

# ============================================
# 	Association & Sale
# ============================================

class AssociationMemberInline(admin.TabularInline):
	model = Association.members.through

class AssociationAdmin(admin.ModelAdmin):
	inlines = (AssociationMemberInline,)
	exclude = ('members',)

class SaleAdmin(admin.ModelAdmin):
	list_display = ('name', 'association', 'is_active', 'public', 'created_at', 'begin_at', 'end_at')
	list_filter = ('is_active', 'public')
	list_editable = tuple()

	fieldsets = (
		(None, 			{ 'fields': ('name', 'description') }),
		('Visibility', 	{ 'fields': ('is_active', 'public') }),
		('Timing', 		{ 'fields': ('begin_at', 'end_at') }),
	)
	add_fieldsets = (
		(None, 			{ 'fields': ('name', 'description', 'association') }),
		('Visibility', 	{ 'fields': ('is_active', 'public') }),
		('Timing', 		{ 'fields': ('begin_at', 'end_at') }),
	)

	search_fields = ('name', 'association')
	ordering = ('begin_at', 'end_at')


admin.site.register(Association, AssociationAdmin)
# admin.site.register(AssociationMember)
admin.site.register(Sale, SaleAdmin)

admin.site.register(Item)
admin.site.register(ItemGroup)
admin.site.register(Order)
admin.site.register(OrderLine)

admin.site.register(Field)
admin.site.register(ItemField)
admin.site.register(OrderLineItem)
admin.site.register(OrderLineField)

