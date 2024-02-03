from product.models import *


def default(request):
  categories = Category.objects.all()
  address = Address.objects.get(user=request.user)


  return{
    'categories':categories,
    'address':address,
  }