from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name='cart'

urlpatterns = [
    path('cart-view',views.view_cart,name='view_cart'),
    path('cart-add/<int:id>/',views.add_cart,name='add_cart'),
    path('cart-add/',views.add_cart,name='add_cart'),
    path('cart-delete/<int:id>/',views.delete_cart,name='delete_cart'),
    path('plus-item/',views.item_plus,name='plus_item'),
    path('minus-item/',views.item_minus,name='minus_item'),
    path('clear_cart/',views.clear_cart,name='clear_cart'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)
   
   
   
    # path('add-to-cart/',views.add_to_cart,name='add-to-cart'),
    # path('cart/',views.cart_view,name='cart'),
    # path('delete-from-cart/',views.delete_item_from_cart,name='delete-from-cart'),
    # path('update-cart/',views.update_cart,name='update-cart'),
   
   