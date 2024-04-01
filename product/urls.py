from django.urls import path, include 
from product.views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'product'

urlpatterns = [
    path('',index, name='index'),
    path('products/',product_list_view, name='product-list'),
    path("products/<int:pid>/<int:cate_id>/", product_detail_view, name="product-detail"),
    path("category/", category_list_view, name="category-list"),
    path("category/<id>/", category_product_list, name="category-product-list"),
    path("search/", search_view, name="search"),
    path("add-review/<int:id>/", ajax_add_review, name="add-review"),
    path("filter-product/", filter_product, name="filter-product"),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)