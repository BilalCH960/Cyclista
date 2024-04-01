from django.contrib import admin
from .models import Cart, Cart_Item

class Cart_ItemInline(admin.TabularInline):
    model = Cart_Item
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'sub_total', 'shipping', 'created_date')
    search_fields = ('user__username',)
    inlines = [Cart_ItemInline]

class Cart_ItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'is_active')
    search_fields = ('cart__user__username', 'product__product_name')

admin.site.register(Cart, CartAdmin)
admin.site.register(Cart_Item, Cart_ItemAdmin)
