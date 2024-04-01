from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_number', 'order_time', 'order_update_time', 'is_complete')
    list_filter = ('is_complete',)
    search_fields = ('user__username', 'order_number')
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'order_item_id', 'order_status', 'order_product', 'quantity', 'product_price', 'ordered_time', 'order_updated_time')
    list_filter = ('order_status',)
    search_fields = ('order__user__username', 'order_product__product_name')

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
