from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from product.models import *
from django.views.decorators.cache import cache_control


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def index(request):
  # products = Product.objects.all()
  products = Product.objects.filter(product_status='published', featured = True)
  


  context = {
    "products":products
  }
  return render(request, 'product/index.html', context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def product_list_view(request):
  products = Product.objects.filter(product_status='published')
  
  
  context = {
    "products":products
  }
  return render(request, 'product/product-list.html', context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def product_detail_view(request, pid):
  product = Product.objects.get(pid=pid)
  # product= get_object_or_404(Product, pid=pid)

  p_image = product.p_images.all()

  context = {
    "p" : product,
    "p_image" : p_image
  }

  return render(request, 'product/product-detail.html', context)