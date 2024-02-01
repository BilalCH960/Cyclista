from django.http import HttpResponse
from django.shortcuts import render
from product.models import *

# Create your views here.

def index(request):
  products = Product.objects.all()
  context = {
    "products":products
  }
  return render(request, 'product/index.html', context)