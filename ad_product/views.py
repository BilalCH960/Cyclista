import uuid
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from .forms import *
from django.db.models import Q
from django.shortcuts import get_object_or_404

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def view_product(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    pro = Product.objects.all() 
    context = {
        'pro' : pro,
    }
    return render (request, 'admin/products/product.html', context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def product_adding(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')


    form = ProductForm()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'the product added succesfully')
            return redirect('ad_product:view_product')
    else:
        form = ProductForm()
    return render(request, 'admin/products/add_product.html',{'form':form} )



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def product_edit(request, id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    pro = get_object_or_404(Product, id=id)
    if request.method=="POST":
        form = ProductForm( request.POST, request.FILES,instance=pro)
        if form.is_valid():
            form.save()
            messages.info(request, f'The product{pro.product_name} has been updated successfully')
            return redirect('ad_product:view_product')
    else:
        form = ProductForm(instance = pro)

        context = {
            "form" : form,
            "pro" : pro
        }
    return render(request, 'admin/products/product_edit.html', context )


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def product_delete(request, id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    pro = Product.objects.get(id =id)
    pro.delete()
    messages.info(request,f"the product variant has been deleted {pro.product_name}")

    return redirect("ad_product:view_product")


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def product_status(request, id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    pro = Product.objects.get(id =id)
    if pro.is_active == True:
        pro.is_active = False
        pro.save()
        messages.info(request,f"the product variant has been set to inactive {pro.product_name}")
    else:
        pro.is_active = True
        pro.save()
        messages.info(request,f"the product variant has been set to active {pro.product_name}")

    return redirect("ad_product:view_product")

#--------------------------------------------------------------------------------------- 


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def product_variant(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    try:
        if request.method == 'POST':
            max_price = request.POST['max_price']
            sale_price =  request.POST['sale_price']
            uu_order_id = int(uuid.uuid4().hex[:8],16)
            uu_order_id = f"#{uu_order_id}"
            model_id = uu_order_id
            stock = request.POST['stock']

            if '-' in str(max_price) or  '-' in str(sale_price) or  '-' in str(stock):
                messages.warning(request,'cant add negative values')
                return redirect('ad_product:product_variant')
            
            if  str(max_price) == '0' or  str(sale_price)=='0' or  str(stock)=='0' :
                messages.warning(request,'cant add only 0 as values ')
                return redirect('ad_product:product_variant')
            
            else:
                images = request.FILES.getlist('images')
                color = get_object_or_404(AttributeValue, id=request.POST['color'])
                # size = get_object_or_404(AttributeValue, id=request.POST['size'])

                variant_new = ProductVariant.objects.create(
                    product = get_object_or_404(Product, id=request.POST['product']),
                    model_id = model_id,
                    color = get_object_or_404(AttributeValue, id=request.POST['color']),
                    # size = size.Attribute_value,
                    max_price = max_price,
                    sale_price = sale_price,
                    stock = stock,
                    description =  request.POST['description'],
                )

                variant_new.save()
                for image in images:
                    VariantImage.objects.create(variant = variant_new, images = image,)
                messages.success(request, f'the product variant has added succesfully')
                return redirect('ad_product:product_variant')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        messages.warning(request,f'{str(e)}')
        return redirect('ad_product:product_variant')
    
    print(request.POST)
    product = Product.objects.filter(is_active = True)
    print(product)
    color = AttributeValue.objects.filter(Q(Attribute_id =1) & Q(is_active = True))
    # size = AttributeValue.objects.filter(Q(Attribute_id =2) & Q(is_active = True))

    context = {
        'product' : product,
        'color' : color,
        # 'size' : size,
            }

    return render(request, 'admin/products/product_varient.html',context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def view_variant(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')

    variant = ProductVariant.objects.all()
    context = {
        'variant' : variant,
    }
    return render (request, 'admin/products/variant_view.html', context)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def variant_status(request, id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    if request.method =="POST":
        var = ProductVariant.objects.get(id = id)
        if var.is_active == True:
            var.is_active = False
            messages.info(request,f"the product variant has been set to inactive { var.product}")
            var.save()
        else:
            var.is_active = True
            messages.info(request,f"the product variant has been set to active { var.product }")
            var.save()


    return redirect("ad_product:view_variant")


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def variant_delete(request,id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    var = ProductVariant.objects.get(id = id)
    var.delete()
    messages.info(request, "Product Variant Deleted Successfully!")
    return redirect("ad_product:view_variant")


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def variant_edit(request,id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    var = get_object_or_404(ProductVariant, id=id)
    cl = var.color.id
    clr = get_object_or_404(AttributeValue, id = cl)
    

    print(var.color.Attribute_value)
    if request.method =="POST":
        # var.size = request.POST['size']
        var.max_price = request.POST['max_price']
        var.sale_price = request.POST['sale_price']
        var.stock = request.POST['stock']
        var.description = request.POST['description']
        var.featured = request.POST.get('featured') == 'on'
        try: 
            var.save()
            if  request.FILES.getlist('images'):
                new_images = request.FILES.getlist('images')
                for image in new_images:
                    VariantImage.objects.create(variant = var, images = image)
            
            messages.success(request, f'the product variant {var.product} has added succesfully')
            return redirect("ad_product:view_variant")
        except:
            pass

    else:
        color = AttributeValue.objects.filter(Q(Attribute_id =1) & Q(is_active = True))
        # size = AttributeValue.objects.filter(Q(Attribute_id =2) & Q(is_active = True))
        context = {
            'var': var,
            'color' : color,
            'clr' : clr,
        }
        return render (request, 'admin/products/variant_edit.html', context)
    


def variant_image_edit(request,id, var_id):
    image = get_object_or_404(VariantImage, id=id, variant = var_id)
    image.delete()
    messages.info(request,'the image has been deleted')
    return redirect('ad_product:variant_edit', id=var_id)


def product_select_variant(request, id):
    variant = ProductVariant.objects.filter(product = id)
    context = {
        'variant':variant,
    }
    return render (request, 'admin/products/variant_view.html', context)
    


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def view_attribute(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    att = AttributeValue.objects.all()

    context = {
        'att' : att,
    }
    return render (request, 'admin/products/attribute/attribute_view.html', context)



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def attribute_status(request, id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    if request.method =="POST":
        att = AttributeValue.objects.get(id = id)
        if att.is_active == True:
            att.is_active=False
            att.save()
            messages.info(request, f'The Attribute {att.Attribute} - {att.Attribute_value}  has been set to inactive')
        else:
            att.is_active=True
            att.save()
            messages.info(request, f'The Attribute {att.Attribute} - {att.Attribute_value}  has been set to active')


    return redirect('ad_product:view_att')



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def attribute_delete(request, id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    att = AttributeValue.objects.get(id = id)
    att.delete()
    messages.info(request, 'The attibute has been deleted')
    return redirect('ad_product:view_att')



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def attribute(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
 

    form = AttributeForm()
    if request.method == "POST":
        form = AttributeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'the attribute added successfully')
            return redirect('ad_product:add_attribute')
    else:
        form = AttributeForm()
    return render(request, 'admin/products/attribute/product_attribute.html', {'form': form})



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def attribute_value(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    form = AttributeValueForm()
    if request.method =="POST":
        form = AttributeValueForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'the attribute value added succesfully')
            return redirect('ad_product:add_attribute_value')
    else:
        form = AttributeValueForm()


    return render (request, 'admin/products/product_values.html',{'form':form})