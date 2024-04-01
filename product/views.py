from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from ad_product.models import Product, ProductVariant, VariantImage, AttributeValue, Attribute
from django.views.decorators.cache import cache_control
from category_manage.models import Category
from django.db.models import Q
from .models import ProductReview
from django.db.models import Avg,Sum,Count
from .forms import ProductReviewForm
from order.models import OrderItem
from django.template.loader import render_to_string



# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def index(request):
  

  # if request.user.is_superuser:
  #       return redirect('admin_side:admin_dash_handler')
  products = ProductVariant.objects.all()
  for product in products:
    if product.stock <  1:
        product.is_active = False
        product.save()

  try:
    products = ProductVariant.objects.filter(is_active = True, featured = True)
    new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:10]
    cat = Category.objects.filter(is_available = True) 
    product_variant_quantities = OrderItem.objects.values('order_product').annotate(total_quantity_sold=Count('quantity'))
    pop = product_variant_quantities.order_by('-total_quantity_sold')


    context = {
      "products":products,
      "new" : new,
      'category' : cat,
      'pop' : pop,

    }
  except Exception as e:
        print(f'the error is {e}')
  return render(request, 'product/index.html', context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def product_list_view(request):
  # products = ProductVariant.objects.filter(product_status='published')
  products = ProductVariant.objects.filter(is_active = True)
  count = ProductVariant.objects.all().count()
  category = Category.objects.all()
  colors = AttributeValue.objects.filter(is_active=True)
  new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:3]
  
  context = {
    "products":products,
    "count":count, 
    "category" : category,
    "colors" : colors,
    "new" : new,
  }
  return render(request, 'product/product-list.html', context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def product_detail_view(request, pid, cate_id):

  user_review_count = 0
  product = ProductVariant.objects.get(id=pid)
  # review of a product
  prod = Product.objects.filter(product_catg = cate_id)
  print(prod)
  product_colors = AttributeValue.objects.filter(productvariant__product_id=product.product_id).distinct()
  review = ProductReview.objects.filter(product=product).order_by("-date")
  # average review
  average = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
  # Product Review Form
  review_form = ProductReviewForm()
  product_ids = [product.id for product in prod]
  prodvariants = ProductVariant.objects.filter(product__id__in=product_ids).exclude(id=pid)
  print(prodvariants)
  make_review = True

  if request.user.is_authenticated:
     user_review_count = ProductReview.objects.filter(user = request.user, product=product).count()

  if user_review_count > 0:
     make_review = False

  context = {
    "make_review" : make_review,
    "p" : product,
    "var" : product_colors,
    "average" : average,
    "rproducts" : prodvariants,
    "review" : review,
    "review_form" : review_form,

  }

  return render(request, 'product/product-detail.html', context)


def category_list_view(request):
  categories = Category.objects.all()
  

  context = {
    "categories" : categories,
  }
  return render(request, 'product/category-list.html', context)


def search_view(request):
  query = request.GET.get('q')

  products = ProductVariant.objects.filter(Q(product__product_name__icontains=query) | Q(description__icontains=query)).order_by("-created_at")
  count = products.count()

  context = {
    "products" : products,
    "query" : query,
    "count" : count
  }
  return render(request, 'product/search.html', context)


def category_product_list(request, id):

  category = Category.objects.get(id=id)
  products = ProductVariant.objects.filter(Q(product_status = "published") | Q(product__product_catg=category))

  context = {
    "category" :   category,
    "products" :   products,

  }
  return render(request, "product/category-product-list.html",context)


def ajax_add_review(request, id):
    product = ProductVariant.objects.get(pk = id)
    user = request.user

    rating = request.POST.get('rating')

    review = ProductReview.objects.create(
        user = user,
        product = product,
        review=request.POST.get('review'),
        rating=rating,
    )

    context = {
        'user' : request.user.username,
        'review' : request.POST['review'],
        'rating' : rating,
        'img' : request.user.userprofile.profile_pic.url
    }

    average_reviews = ProductReview.objects.filter(product= product).aggregate(rating=Avg('rating'))

    return JsonResponse(
        {
            'bool' : True,
            'context' : context,
            'avg_reviews' : average_reviews,
}
    )


def filter_product(request):
    categories = request.GET.getlist('category[]')
    colors = request.GET.getlist('color[]')

    products = ProductVariant.objects.filter(is_active=True).order_by("-id").distinct()

    if len(categories) > 0:
      products = products.filter(product__product_catg__id__in=categories).distinct()

    if len(colors) > 0:
      products = products.filter(color__id__in=colors).distinct()

    data = render_to_string("product/async/product-list.html", {"products":products})
    return JsonResponse({"data" : data})


