from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'order'

urlpatterns = [
    path('order-manage-view', views.order_view, name="order_view"),
    path('place_order', views.place_order, name="place_order"),
    path('view-order_details', views.order_details, name="order_status"),
    path('download-invoice/<int:order_number>/', views.download_invoice, name='download_invoice'),
    path('view-order_listing/<int:id>', views.order_listing, name="order_listing"),
    path('view_order/<int:id>/', views.user_orders, name='view-orders'),
    path('cancel_order_req/<int:id>/', views.cancel_order_req, name="cancel_order_req"),
    path('view-cancel_order_request/<int:id>/', views.cancel_order, name="cancel_order"),
    path('return_order_req/<int:id>/', views.return_order_req, name="return_order_req"),
    path('view-return_order_request/<int:id>/', views.return_order, name="return_order"),
    path('view-admin_order', views.admin_order_view, name="admin_order_view"),
    path('admin/orders/filter/', views.filter_orders_by_date, name='filter_orders_by_date'),
    path('admin/orders/filter/pdf/', views.filter_orders_pdf, name='filter_orders_pdf'),
    path('admin_order_item_details/<int:id>/', views.admin_order_item_details, name="admin_order_item_details"),
    path('admin_order_item_view/<int:id>/', views.admin_order_item_view, name="admin_order_item_view"),
    path('admin_order_status/', views.admin_order_status, name="admin_order_status"), 
    path('admin_order_status_all/', views.admin_order_status_all, name="admin_order_status_all"), 
    path('user_details_views/<int:id>', views.user_details_views, name="user_details_views"),
   
    path('payment/success',views.payment_success,name='success'),
    path('payment/failed',views.payment_failed,name='failed'),

    


    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_URL)