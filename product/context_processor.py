from category_manage.models import *
from account.models import *
from ad_product.models import *



def default(request):
  categories = Category.objects.all()
  colors = AttributeValue.objects.filter(is_active=True)

  try:
    address = Address.objects.get(user=request.user)
  except:
    address = None


  return{
    'categories':categories,
    'address':address,
    'colors':colors,
  }