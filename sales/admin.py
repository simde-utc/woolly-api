from django.utils.safestring import mark_safe
from django.db.models import Count
from django.contrib import admin

from core.helpers import adaptable_editability_fields
from .models import (
    Association, Sale, ItemGroup, Item,
    OrderStatus, Order, OrderLine, OrderLineItem,
    Field, ItemField, OrderLineField,
)


# ============================================
#   Inlines
# ============================================

class ItemFieldInline(admin.TabularInline):
    model = ItemField
    extra = 0


class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0
    readonly_fields = ('id',)


class OrderLineFieldInline(admin.TabularInline):
    model = OrderLineField
    extra = 0
    readonly_fields = ('id',)


# --------------------------------------------
#   Associations
# --------------------------------------------

class AssociationAdmin(admin.ModelAdmin):
    list_display = ('shortname', 'fun_id')
    exclude = ('members',)
    search_fields = ('shortname', 'fun_id')
    ordering = ('shortname',)


class SaleAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_items_count=Count("items", distinct=True))
        return queryset

    # Displayers
    def number_of_items(self, obj) -> int:
        return obj._items_count

    list_display = ('name', 'association', 'is_active', 'is_public', 'number_of_items', 'created_at', 'begin_at', 'end_at')
    list_filter = ('is_active', 'is_public')
    list_editable = tuple()

    def get_readonly_fields(self, request, obj=None):
        return adaptable_editability_fields(request, obj, ('association',))

    fieldsets = (
        (None,          { 'fields': ('name', 'description', 'association', 'max_item_quantity') }),
        ('Visibility',  { 'fields': ('is_active', 'is_public') }),
        ('Timing',      { 'fields': ('begin_at', 'end_at') }),
    )

    search_fields = ('name', 'association')
    ordering = ('begin_at', 'end_at')


# --------------------------------------------
#   Items
# --------------------------------------------

class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'sale', 'group', 'is_active',
        'quantity', 'quantity_left', 'usertype', 'price', 'max_per_user'
    )
    list_filter = ('is_active', 'sale', 'group', 'usertype')
    list_editable = tuple()

    inlines = (ItemFieldInline,)
    exclude = ('fields',)
    fieldsets = (
        (None,              { 'fields': ('name', 'description', 'price', 'sale', 'group') }),
        ('Accessibility',   { 'fields': ('is_active', 'quantity', 'max_per_user', 'usertype') }),
        ('Payment',         { 'fields': ('nemopay_id',) }),
    )

    search_fields = ('name', 'sale', 'group')
    ordering = ('sale', 'name', 'usertype')


# --------------------------------------------
#   Orders
# --------------------------------------------

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'owner', 'get_status', 'get_uuids', 'created_at')
    list_filter = ('status', 'sale__name')
    list_editable = tuple()

    def get_uuids(self, order: Order) -> int:
        return mark_safe("<br>".join(str(orderlineitem.id)
                                     for orderline in order.orderlines.all()
                                     for orderlineitem in orderline.orderlineitems.all()))

    get_uuids.short_description = 'UUIDs'
    get_uuids.admin_order_field = 'uuids'

    def get_status(self, order: Order) -> str:
        if order.status in OrderStatus.VALIDATED_LIST.value:
            color = "green"
        elif order.status in OrderStatus.CANCELLED_LIST.value:
            color = "red"
        else:
            color = "black"
        return mark_safe("<span style='color: %s;'>%s</span>" % (color, order.get_status_display()))

    def get_readonly_fields(self, request, obj=None):
        return adaptable_editability_fields(request, obj, ('sale', 'owner'))
    fieldsets = (
        (None,              { 'fields': ('sale', 'owner', 'status') }),
        ('Payment',         { 'fields': ('tra_id',) }),
    )

    search_fields = ('sale__name', 'owner__email', 'orderlines__orderlineitems__id')
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

    def get_uuids(self, orderline):
        return mark_safe("<br>".join(str(orderlineitem.id)
                                     for orderlineitem in orderline.orderlineitems.all()))

    get_uuids.short_description = 'UUIDs'
    get_uuids.admin_order_field = 'uuids'

    list_display = ('id', 'order_id', 'order_status', 'owner', 'sale_name', 'item_name', 'get_uuids', 'quantity')

    def get_readonly_fields(self, request, obj=None):
        return adaptable_editability_fields(request, obj, ('order', 'item'))

    inlines = (OrderLineItemInline,)
    fieldsets = (
        (None, { 'fields': ('order', 'item', 'quantity') }),
    )

    search_fields = ('item__name', 'order__owner__email', 'order__sale__name')
    list_filter = ('order__status', 'order__sale__name')


class OrderLineItemAdmin(admin.ModelAdmin):
    # Displayers
    def orderline_id(self, obj):
        return obj.orderline.id

    def order_id(self, obj):
        return obj.orderline.order.id

    def owner(self, obj):
        return obj.orderline.order.owner

    def sale(self, obj):
        return obj.orderline.order.sale

    list_display = ('id', 'orderline_id', 'order_id', 'owner', 'sale')
    list_filter = ('orderline__order__sale',)  # TODO Not working
    inlines = (OrderLineFieldInline,)

    def get_readonly_fields(self, request, obj=None):
        return adaptable_editability_fields(request, obj, ('orderline',), ('id',))
    search_fields = ('id', 'orderline__order__owner__email', 'orderline__order__sale__name')


# --------------------------------------------
#   Fields
# --------------------------------------------

class FieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'default')
    list_filter = ('type',)
    search_fields = ('name',)


class OrderLineFieldAdmin(admin.ModelAdmin):
    # Displayers
    def orderlineitem_id(self, obj):
        return obj.orderlineitem.id

    list_display = ('id', 'orderlineitem_id', 'field', 'value')
    list_filter = ('field',)

    def get_readonly_fields(self, request, obj=None):
        return adaptable_editability_fields(request, obj, ('orderlineitem', 'field'))
    fieldsets = (
        (None, { 'fields': ('orderlineitem', 'field', 'value') }),
    )
    search_fields = ('value', 'orderlineitem__id,' 'orderlineitem__orderline__owner__email')


admin.site.register(Association, AssociationAdmin)
admin.site.register(Sale, SaleAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemGroup)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)

admin.site.register(Field, FieldAdmin)
# admin.site.register(ItemField)
admin.site.register(OrderLineItem, OrderLineItemAdmin)
admin.site.register(OrderLineField, OrderLineFieldAdmin)
