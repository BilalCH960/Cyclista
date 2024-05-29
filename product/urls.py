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
    path("varnts/<int:pid>/<int:avid>/", varnts, name="varnts"),

    ### sort and filter
    path("featured/", sort_featured, name="featured"),
    path("price_asc/", sort_price_asc, name="price_asc"),
    path("price_desc/", sort_price_desc, name="price_desc"),
    path("name_asc/", sort_name_asc, name="name_asc"),
    path("name_desc/", sort_name_desc, name="name_desc"),
    path("add-review/<int:id>/", ajax_add_review, name="add-review"),
    path("filter-product/", filter_product, name="filter-product"),

    ###  wishlist
    path('add-to-wishlist/<int:prid>/<int:cid>/', add_wishlist, name='add_wishlist'),
    path('view-from-wishlist/', view_wishlist, name='wishlist'),
    path('delete-from-wishlist/<int:prid>/', delete_wishlist, name='delete_wishlist'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)