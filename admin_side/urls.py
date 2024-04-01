from django.urls import path
from . import views

app_name = 'admin_side'


urlpatterns = [
    path('logout/', views.logout_handler, name='logout'),
    path('login/', views.superuser_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_customer/', views.admin_user_handler, name='admin_user_manage'),
    path('customer_status/<int:user_id>', views.customer_status, name='customer_status'),
    path('adsignout/', views.logout_view, name='adsign-out'),


]
