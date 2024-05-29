from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from ad_product.models import Product, ProductVariant, VariantImage, AttributeValue, Attribute
from django.views.decorators.cache import cache_control
from category_manage.models import Category
from django.db.models import Q
from .models import ProductReview
from django.db.models import Avg,Sum,Count
from .forms import ProductReviewForm
from .models import Wishlist
from django.contrib import messages
from order.models import OrderItem
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required



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
    products = ProductVariant.objects.filter(is_active = True, featured = True, soft_delete = False, product__soft_delete=False)
    new = ProductVariant.objects.filter(Q(is_active = True)&Q(soft_delete = False, product__soft_delete=False)).order_by("-updated_at")[:10]
    cat = Category.objects.filter(is_available = True) 
    product_variant_quantities = OrderItem.objects.values('order_product').annotate(total_quantity_sold=Sum('quantity'))
    most_sold_variants = product_variant_quantities.order_by('-total_quantity_sold')
    pop = ProductVariant.objects.filter(soft_delete = False, product__soft_delete=False, id__in=most_sold_variants.values_list('order_product', flat=True))



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
  products_list = ProductVariant.objects.filter(is_active = True, soft_delete = False, product__soft_delete=False)
  paginator = Paginator(products_list, 3)
  count = ProductVariant.objects.filter(is_active = True, soft_delete = False, product__soft_delete=False).count()
  category = Category.objects.all()
  colors = AttributeValue.objects.filter(is_active=True)
  new = ProductVariant.objects.filter(is_active = True, soft_delete=False,  product__soft_delete=False,).order_by("-updated_at")[:3]
  print(f'category={category}')
  
  page = request.GET.get('page')

  try:
      products = paginator.page(page)
  except PageNotAnInteger:
      products = paginator.page(1)
  except EmptyPage:
      products = paginator.page(paginator.num_pages)

  context = {
    "products":products,
    "count":count, 
    "category" : category,
    "colors" : colors,
    "new" : new,
  }
  return render(request, 'product/product-list.html', context)



def sort_featured(request):
  products_list = ProductVariant.objects.filter(featured = True)
  paginator = Paginator(products_list, 3)
  category = Category.objects.all()
  new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:3]

  page = request.GET.get('page')

  try:
      products = paginator.page(page)
  except PageNotAnInteger:
      products = paginator.page(1)
  except EmptyPage:
      products = paginator.page(paginator.num_pages)

  context = { 
    "products" : products,
    "category" : category,
    "new" : new,
              }
  return render(request, 'product/product-list.html', context)



def sort_price_asc(request):
  products_list = ProductVariant.objects.filter(is_active=True).order_by("sale_price")
  paginator = Paginator(products_list, 3)
  category = Category.objects.all()
  new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:3]

  page = request.GET.get('page')

  try:
      products = paginator.page(page)
  except PageNotAnInteger:
      products = paginator.page(1)
  except EmptyPage:
      products = paginator.page(paginator.num_pages)

  context = { 
    "products" : products,
    "category" : category,
    "new" : new,
              }
  return render(request, 'product/product-list.html', context)



def sort_price_desc(request):
  products_list = ProductVariant.objects.filter(is_active=True).order_by("-sale_price")
  paginator = Paginator(products_list, 3)
  category = Category.objects.all()
  new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:3]

  page = request.GET.get('page')

  try:
      products = paginator.page(page)
  except PageNotAnInteger:
      products = paginator.page(1)
  except EmptyPage:
      products = paginator.page(paginator.num_pages)

  context = { 
    "products" : products,
    "category" : category,
    "new" : new,
              }
  return render(request, 'product/product-list.html', context)


def sort_name_asc(request):
  products_list = ProductVariant.objects.filter(is_active=True).order_by("product")
  paginator = Paginator(products_list, 3)
  category = Category.objects.all()
  new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:3]

  page = request.GET.get('page')

  try:
      products = paginator.page(page)
  except PageNotAnInteger:
      products = paginator.page(1)
  except EmptyPage:
      products = paginator.page(paginator.num_pages)

  context = { 
    "products" : products,
    "category" : category,
    "new" : new,
              }
  return render(request, 'product/product-list.html', context)



def sort_name_desc(request):
  products_list = ProductVariant.objects.filter(is_active=True).order_by("-product")
  paginator = Paginator(products_list, 3)
  category = Category.objects.all()
  new = ProductVariant.objects.filter(is_active = True).order_by("-updated_at")[:3]

  page = request.GET.get('page')

  try:
      products = paginator.page(page)
  except PageNotAnInteger:
      products = paginator.page(1)
  except EmptyPage:
      products = paginator.page(paginator.num_pages)

  context = { 
    "products" : products,
    "category" : category,
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
  product_colors = AttributeValue.objects.filter(productvariant__product_id=product.product_id, productvariant__soft_delete = False).distinct()
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

  products = ProductVariant.objects.filter(product__product_name__icontains=query).order_by("-created_at")
  count = products.count()

  context = {
    "products" : products,
    "query" : query,
    "count" : count
  }
  return render(request, 'product/search.html', context)


def category_product_list(request, id):

  category = Category.objects.get(id=id)
  products = ProductVariant.objects.filter(
    Q(product_status="published") | Q(product__product_catg=category),
    soft_delete=False,  product__soft_delete=False,
)

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


def varnts(request, pid, avid):
    product = get_object_or_404(Product, id = pid)
    attribute_value = get_object_or_404(AttributeValue, id=avid)
    
    product_variant = get_object_or_404(ProductVariant, product=product, color=attribute_value, soft_delete = False)

    print(f'hi{product}')
    print(attribute_value)
    print(product_variant)
    category_id = product.product_catg_id
    
    # Redirect to the product detail page with product variant ID and category ID
    return redirect('product:product-detail', pid=product_variant.id, cate_id=category_id)
    
    

    



#### Wishlist ####8989
@login_required
def add_wishlist(request,prid, cid):
    if not request.user.is_authenticated:
      return redirect('product:login')
    product = ProductVariant.objects.get(id = prid)
    if Wishlist.objects.filter(user = request.user, wish_item = product).exists():
        messages.info(request,"This item is already in your wish list")
    else:
        Wishlist.objects.create(user = request.user, wish_item = product)
        messages.success(request, "the product added to Wishlist successfully")
        return redirect('product:product-list')
    return redirect('product:product-detail', pid=prid , cate_id=cid) 


@login_required
def view_wishlist(request):
    if not request.user.is_authenticated:
      return redirect('product:login')
    wishlist = Wishlist.objects.filter(user = request.user)
    user_wishlist = [item.wish_item for item in wishlist]
    
    context = {
        'items' : user_wishlist,
    }
    

    return render(request, 'user/wishlist.html' ,context)


@login_required
def delete_wishlist(request,prid):
    product = Wishlist.objects.get(user = request.user, wish_item_id= prid)
    messages.warning(request,"item has been removed from wishlist")
    product.delete()
    return redirect('product:wishlist')

