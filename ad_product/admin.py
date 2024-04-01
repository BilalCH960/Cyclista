from django.contrib import admin
from .models import Product, ProductImages, Attribute, AttributeValue, ProductVariant, VariantImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_catg', 'created_at', 'updated_at', 'is_active')
    list_filter = ('product_catg', 'is_active')
    search_fields = ('product_name',)
    prepopulated_fields = {'product_slug': ('product_name',)}

class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('images', 'product', 'date')

class AttributeAdmin(admin.ModelAdmin):
    list_display = ('attribute_name', 'is_active')

class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('Attribute', 'Attribute_value', 'is_active')

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'model_id', 'color', 'max_price', 'sale_price', 'stock', 'product_status', 'is_active', 'created_at', 'updated_at')
    list_filter = ('product_status', 'is_active', 'created_at', 'updated_at')
    list_editable = ('max_price', 'sale_price', 'stock', 'product_status', 'is_active')

class VariantImageAdmin(admin.ModelAdmin):
    list_display = ('variant', 'images')

# Register your models with the custom admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImages, ProductImagesAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(VariantImage, VariantImageAdmin)
