from django.contrib import admin
from .models import *



class ProductReviewAdmin(admin.ModelAdmin):
  list_display = ['user', 'product', 'review', 'rating']


class WishlistAdmin(admin.ModelAdmin):
  list_display = ['user', 'wish_item', 'date']




admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
# admin.site.register(Address, AddressAdmin)

