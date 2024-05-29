from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from .models import Category, CategoryOffer
from django.contrib import messages
from .forms import CategoryOfferForm
from decimal import Decimal
from ad_product.models import Product, ProductVariant





@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def category_main(request):
    try:
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect('product:index')       
    except:
        pass
    cat = Category.objects.all()
    context = {
        'categories': cat
    }
    print(cat)
    return render(request, 'admin/category/category.html', context)





@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def add_category(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('product:index')
    if request.method == 'POST':
        name = request.POST.get('category_name')
        if name.strip() == "":
            messages.error(request,'Category name is required')
            return redirect('category_manage:category_handler')
        description = request.POST.get('description')
        if description.strip() == "":
            messages.error(request,'Category description is required')
            return redirect('category_manage:category_handler')
        images = request.FILES.get('imgs')
        print(name)
        print(description)
        print(images)


        Category.objects.create(
            category_name=name,
            description=description,
            category_img=images
        )
        messages.success(request,'Category added successfully')
   
    print(Category.objects.get(category_name=name))

    return redirect('category_manage:category_handler')


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def delete_category(request, slug):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('product:index')
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        messages.warning(request, "Category does not exist.")
        return redirect('category_manage:category_list')
    category.delete()
    messages.warning(request, "Category Deleted ❌")
    return redirect('category_manage:category_handler')


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def edit_category(request, id):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('product:index')
    
    cat = get_object_or_404(Category, id=id)

    if request.method == "POST":
        cat.category_name = request.POST.get('category_name')
        cat.description = request.POST.get('description')
        if request.FILES.get('imgs'):
            cat.category_img = request.FILES.get('imgs')

        try:
            cat.save()
            messages.success(request, f'The category {cat.category_name} has been updated successfully')
            return redirect('category_manage:category_handler')
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
            # Handle the error as needed

    context = {'cat': cat}
    return render(request, 'admin/category/category_edit.html', context)
        
@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def status_category(request, id):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('product:index')
    if request.method == "POST":
        cat = get_object_or_404(Category, id=id)
        if cat.is_available == True:
            cat.is_available = False
            cat.save()
            messages.info(request,'The status has been changed to inactive successfully')
        else:
            cat.is_available =True
            cat.save()
            messages.info(request,'The status has been changed active successfully')
        return redirect('category_manage:category_handler')
    


def view_categoryoffer(request):

    context = {
        'offers': CategoryOffer.objects.all(),
    }

    return render(request, 'admin/category/offer_management.html', context)

def status_categoryoffer(request, id):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('product:index')
    if request.method == "POST":
        cat = get_object_or_404(CategoryOffer, id=id)
        if cat.is_active == True:
            cat.is_active = False
            make_price_again(cat.category_name.pk, cat.discount)
            cat.save()
            messages.info(request,'The status has been changed to inactive successfully')
        else:
            cat.is_active =True
            make_price(cat.category_name.pk, cat.discount)
            cat.save()
            messages.info(request,'The status has been changed active successfully')
        return redirect('category_manage:view_categoryoffer') 


def add_categoryoffer(request):
    if not request.user.is_superuser:
        return redirect('product:index')

    if request.method == "POST":
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)  # Use commit=False to modify before saving
            offer.valid_to = form.cleaned_data['valid_to']
            offer.save()  # Save the instance first
            
            category = form.cleaned_data['category_name']
            discount = form.cleaned_data['discount']
            
            # Apply discount to all product variants within the selected category
            products = Product.objects.filter(product_catg__category_name=category)
            for product in products:
                variants = ProductVariant.objects.filter(product=product)
                for variant in variants:
                    variant.sale_price = variant.sale_price - discount
                    variant.save()  # Save each variant after adjusting price
                    
            messages.success(request, "The Category Offer has been created successfully.")
            return redirect("category_manage:view_categoryoffer")
        else:
            messages.warning(request, "Please correct the form errors.")
    else:
        form = CategoryOfferForm()

    return render(request, 'admin/category/add_category_offer.html', {'form': form})


def delete_categoryoffer(request, id):
    cate = CategoryOffer.objects.get(pk=id)
    category = cate.category_name
    product = Product.objects.filter(product_catg = category)
    for p in product:
        variants = ProductVariant.objects.filter(product = p)
    
        for variant in variants:
            variant.sale_price = variant.sale_price + cate.discount
            variant.save()  # Update the sale_price to max_price
        
    cate.delete()
    messages.warning(request, 'The offer has been deleted')
    return redirect('category_manage:view_categoryoffer')



def edit_categoryoffer(request, id):
    cate = CategoryOffer.objects.get(pk=id)
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount'))
            dis = cate.discount
            cate.discount = amount
            cate.is_active = False
            cate.save()
            
            # Calculate the new sale price for each product variant in the category
            # This assumes that the discount should be applied similarly to the add_categoryoffer function
            products = Product.objects.filter(product_catg__category_name=cate.category_name)
            for product in products:
                variants = ProductVariant.objects.filter(product=product)
                for variant in variants:
                    # Update the sale_price to reflect the new discount
                    variant.sale_price = variant.sale_price + dis
                    variant.sale_price = variant.sale_price - amount
                    variant.save()  # Save each variant after adjusting price
                    
            messages.info(request, 'The changes have been saved.')
            return redirect('category_manage:view_categoryoffer')
        except Exception as e:
            print(f'The error is {e}')
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        # Render the template with the existing category offer details
        return render(request, 'admin/category/edit_category_offer.html', {'cate': cate})




def make_price(id, discount):
    for product in Product.objects.filter(product_catg = id):
        for variant in ProductVariant.objects.filter(product = product):
            variant.sale_price = variant.sale_price - discount
            variant.save()

def make_price_again(id, discount):
    for product in Product.objects.filter(product_catg = id):
        for variant in ProductVariant.objects.filter(product = product):
            variant.sale_price = variant.sale_price + discount
            variant.save()