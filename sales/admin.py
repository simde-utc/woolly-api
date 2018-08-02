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

	readonly_fields = ('association',)
	fieldsets = (
		(None, 			{ 'fields': ('name', 'description', 'association') }),
		('Visibility', 	{ 'fields': ('is_active', 'public') }),
		('Timing', 		{ 'fields': ('begin_at', 'end_at') }),
	)

	search_fields = ('name', 'association')
	ordering = ('begin_at', 'end_at')


# ============================================
# 	Item & ItemGroup
# ============================================

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'sale', 'group', 'is_active', 'quantity', 'usertype', 'price', 'max_per_user')
	list_filter = ('is_active', 'sale', 'group', 'usertype')
	list_editable = tuple()

	readonly_fields = ('sale',)
	fieldsets = (
		(None, 				{ 'fields': ('name', 'description', 'sale', 'group') }),
		('Accessibility', 	{ 'fields': ('is_active', 'quantity', 'max_per_user', 'usertype') }),
		('Payment', 		{ 'fields': ('nemopay_id',) }),
	)

	search_fields = ('name', 'sale', 'group')
	ordering = ('sale', 'name', 'usertype')


# ============================================
# 	Order & OrderLine
# ============================================

class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'sale', 'owner', 'status', 'created_at')
	list_filter = ('status', 'sale', 'owner')
	list_editable = tuple()

	readonly_fields = ('sale', 'owner')
	fieldsets = (
		(None, 				{ 'fields': ('sale', 'owner', 'status') }),
		('Payment', 		{ 'fields': ('tra_id',) }),
	)

	search_fields = ('sale', 'owner')
	ordering = ('sale', 'owner', 'created_at')

class OrderLineAdmin(admin.ModelAdmin):
	# Displayers
	def order_id(self, obj):
		return obj.order.id
	def order_status(self, obj):
		return obj.order.get_status_display()
	def sale_name(self, obj):
		return obj.order.sale.name
	def item_name(self, obj):
		return obj.item.name
	def owner(self, obj):
		return obj.order.owner

	list_display = ('id', 'order_id', 'order_status', 'owner', 'sale_name', 'item_name', 'quantity')
	readonly_fields = ('order', 'item')

	fieldsets = (
		(None, { 'fields': ('order', 'item', 'quantity') }),
	)

	search_fields = ('item__name', 'order__owner__email', 'order__sale__name')


admin.site.register(Association, AssociationAdmin)
# admin.site.register(AssociationMember)
admin.site.register(Sale, SaleAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemGroup)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)

admin.site.register(Field)
admin.site.register(ItemField)
admin.site.register(OrderLineItem)
admin.site.register(OrderLineField)

