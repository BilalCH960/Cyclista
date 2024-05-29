from django.urls import path
from wallet import views

app_name = 'wallet'


urlpatterns = [
    
    path('wallet-view', views.wallet_view, name='wallet_view'),
    # path('get_refferal_code', views.get_refferal_code, name='get_refferal_code'),



    


]
