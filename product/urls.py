from django.urls import path, include 
from product.views import *

app_name = 'product'

urlpatterns = [
    path('',index, name='index'),
    path('products/',product_list_view, name='product-list'),
    path("products/<pid>/", product_detail_view, name="product-detail")
]