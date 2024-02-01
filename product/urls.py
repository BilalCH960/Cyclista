from django.urls import path, include 
from product.views import *

app_name = 'product'

urlpatterns = [
    path('',index, name='index'),
]