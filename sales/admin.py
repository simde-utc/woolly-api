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


# ============================================
# 	Item & Order
# ============================================

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'sale', 'group', 'is_active', 'quantity', 'usertype', 'price', 'max_per_user')
	list_filter = ('is_active', 'sale', 'group', 'usertype')
	list_editable = tuple()

	fieldsets = (
		(None, 				{ 'fields': ('name', 'description', 'group') }),
		('Accessibility', 	{ 'fields': ('is_active', 'quantity', 'max_per_user', 'usertype') }),
		('Payment', 		{ 'fields': ('nemopay_id',) }),
	)
	add_fieldsets = (
		(None, 				{ 'fields': ('name', 'description', 'sale', 'group') }),
		('Accessibility', 	{ 'fields': ('is_active', 'quantity', 'max_per_user', 'usertype') }),
		('Payment', 		{ 'fields': ('nemopay_id',) }),
	)

	search_fields = ('name', 'sale', 'group')
	ordering = ('sale', 'name', 'usertype')




admin.site.register(Association, AssociationAdmin)
# admin.site.register(AssociationMember)
admin.site.register(Sale, SaleAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemGroup)
admin.site.register(Order)
admin.site.register(OrderLine)

admin.site.register(Field)
admin.site.register(ItemField)
admin.site.register(OrderLineItem)
admin.site.register(OrderLineField)

