# from datetime import datetime as dt
from django.shortcuts import render, redirect, get_object_or_404
# from django.views.decorators.cache import cache_control
from django.contrib import messages
from cart.models import Cart_Item,Cart
from django.db.models import Q
from ad_product.models import ProductVariant
from decimal import Decimal
from django.http import JsonResponse
from django.template.loader import render_to_string





def view_cart(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:admin_login_handler')
        return redirect('user_side:landing')

    cart, check_cart = Cart.objects.get_or_create(user=request.user)
    cart_items = Cart_Item.objects.filter(cart=cart).order_by('id')
 
    subtotal = sum(item.product.sale_price * item.quantity for item in cart_items)
    shipping = 0
    total = Decimal(subtotal)
    count = Cart_Item.objects.all().count()

    # checking if the user can get free delivery
    if subtotal < 200000:
        shipping = (subtotal * Decimal('0.1')) / 100
        total += shipping  # Include shipping in the total

    if request.method == 'POST':
        if total != 0:
            cart.sub_total = subtotal
            cart.total = total
            cart.shipping = shipping
            cart.save()
            return redirect('cart:view_cart')

    # Check if the cart is empty and update the Cart model
    if not cart_items:
        cart.total = None
        cart.sub_total = None
        cart.shipping = None
        cart.save()
        messages.info(request,'Cart is Running on Low')

        
    context = {
        'itemtotlal' : subtotal,
        'item': cart_items,  # Renamed 'item' to 'items' for clarity
        'pro_subtotal': cart.sub_total if cart.sub_total else subtotal,
        'shipping': cart.shipping if cart.shipping else shipping,
        'total': cart.total if cart.total else total,
        'cart': Cart.objects.filter(user=request.user),
        'count':count,
    }
    return render(request, 'user/cart.html', context)







def add_cart(request, id=None):
    if request.user.is_superuser:
        return JsonResponse({'error': 'User not authorized'}, status=403)

    product_quantity = int(request.POST.get('prod_qty')) if request.POST.get('prod_qty') else 1
    product_id = int(request.POST.get('prod_id')) if request.POST.get('prod_id') else id
    product = get_object_or_404(ProductVariant, id = product_id)
    cart, check_cart = Cart.objects.get_or_create(user=request.user)
    try:
        item_check = Cart_Item.objects.get(cart=cart, product=product)
        print(f'helooo{item_check}')
        if product_quantity > product.stock :
            messages.warning(request, "can't add that many due to stock insufficient")
            return redirect('cart:view_cart')
        elif item_check.quantity + product_quantity > product.stock:
             
            messages.warning(request, 'cant add that many due to stock insufficient')
            return redirect('cart:view_cart')
        else:
            
            item_check.quantity += product_quantity if product_quantity else 1
            item_check.save()
            cart_item = Cart_Item.objects.filter(cart = cart)
            subtotal = sum(item.product.sale_price * item.quantity for item in cart_item)
            shipping = 0
            if subtotal <200000:
                shipping = (subtotal * Decimal('0.1')) / 100
            cart.sub_total = subtotal
            cart.total = subtotal if subtotal else 0
            cart.total += shipping if shipping else 0
            cart.shipping = shipping if shipping else 0
            cart.save()
            messages.success(request, 'The product is in the cart')
            return redirect("cart:view_cart")
    except Cart_Item.DoesNotExist:
        Cart_Item.objects.create(cart=cart, product=product, quantity=product_quantity if product_quantity else 1)
        cart_item = Cart_Item.objects.filter(cart = cart)
        subtotal = sum(item.product.sale_price * item.quantity for item in cart_item)
        shipping = 0
        if subtotal <200000:
            shipping = (subtotal * Decimal('0.1')) / 100
        cart.sub_total = subtotal
        cart.total = subtotal if subtotal else 0
        cart.total += shipping if shipping else 0
        cart.shipping = shipping if shipping else 0
        cart.save()  
        messages.success(request, 'The item has been added to the cart')

        return redirect("cart:view_cart")





def delete_cart(request,id):
    cart_item = Cart_Item.objects.filter(id = id)
    if cart_item:
        cart_item.delete()
        messages.info(request, f"the item has been deleted from cart")
    myCart =Cart.objects.get(user = request.user)
    del_cart = Cart_Item.objects.filter(cart =myCart)
    subtotal = sum(item.product.sale_price * item.quantity for item in del_cart) 
    product_per_price = subtotal
    shipping = Decimal(0)
    if subtotal < 200000:
        shipping = (subtotal * Decimal('0.1'))/100
    myCart.sub_total = product_per_price if product_per_price else 0
    myCart.total = subtotal
    myCart.total += shipping if shipping else 0
    myCart.shipping = shipping if shipping else 0
    myCart.save()
    if del_cart is None:
        myCart.total = None
        myCart.sub_total = None
        myCart.shipping = None
    return redirect('cart:view_cart')   

def item_plus(request):
   
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        try:
            cart = get_object_or_404(Cart, user = request.user)
            id = request.POST.get('cart_id')
            cart_item = get_object_or_404(Cart_Item, cart = cart, id = id)
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            subtotal = Decimal(0)   
            cart_item = Cart_Item.objects.filter(cart = cart)
            subtotal = sum(item.product.sale_price * item.quantity for item in cart_item) 
            product_per_price = subtotal
            shipping = Decimal(0)
            if subtotal < 200000:
                shipping = (subtotal * Decimal('0.1'))/100
        
            cart.sub_total = product_per_price if product_per_price else 0
            cart.total = subtotal
            cart.total += shipping if shipping else 0
            cart.shipping = shipping if shipping else 0
            cart.save()
            quantity = [{'id': item.id, 'quantity': item.quantity} for item in cart_item]
            data = {
                'quantity' : quantity,
                'subtotal' : f'₹ {product_per_price: .2f}',
                'shipping': f'₹ {shipping:.2f}' if shipping else 'Free Shipping',
                'total': f'₹ {cart.total:.2f}',
            }
            return JsonResponse(data)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An error occurred: {str(e)}")
            messages.info(request, 'Cant add more product quantity than its products stock')
    # return JsonResponse({'error': 'Invalid request'}, status=400)
      

def item_minus(request):
   
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        try:
            cart = get_object_or_404(Cart, user = request.user)
            id = request.POST.get('cart_id')
            cart_item = get_object_or_404(Cart_Item, cart = cart, id = id)
            print(cart_item.product.stock)
            print(cart_item.quantity)
            if cart_item.quantity > 1 and cart_item.quantity <= cart_item.product.stock:
                cart_item.quantity -= 1
                cart_item.save()


            subtotal = Decimal(0)   
            cart_item = Cart_Item.objects.filter(cart = cart)
            subtotal = sum(item.product.sale_price * item.quantity for item in cart_item)   
            cart.sub_total = subtotal
            product_per_price = subtotal
            shipping = Decimal(0)
            if subtotal < 200000:
                shipping = (subtotal * Decimal('0.1'))/100
            cart.sub_total = product_per_price if product_per_price else 0
            cart.total = subtotal
            cart.total += shipping if shipping else 0
            cart.shipping = shipping if shipping else 0
            cart.save()
            quantity = [{'id': item.id, 'quantity': item.quantity} for item in cart_item]
            data = {
                'quantity' : quantity,
                'subtotal' : f'₹ {product_per_price: .2f}',
                'shipping': f'₹ {shipping:.2f}' if shipping else 'Free Shipping',
                'total': f'₹ {cart.total:.2f}',
            }
            return JsonResponse(data)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'error': 'An error occurred'}, status=500)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)


def clear_cart(request):
    cart = get_object_or_404(Cart, user = request.user)
    cart_item = Cart_Item.objects.filter(cart=cart)
    cart_item.delete()
    cart.save()
    messages.info(request,'all the cart items have been deleted')
    return redirect('cart:view_cart')



















# def add_to_cart(request):
#     cart_product = {}

#     cart_product[str(request.GET['id'])] = {
#         'title': request.GET['title'],
#         'qty' : request.GET['qty'],
#         'price' : request.GET['price'],
#         'image' : request.GET['image'],
#         'pid' : request.GET['pid'],
#         'id' : request.GET['id'],
#     }

#     # ////
#     product_qty = int(request.GET.get('qty'))
#     product_id = int(request.GET.get('id'))
#     product = get_object_or_404(ProductVariant, id = product_id)
#     cart, check_cart = Cart.objects.get_or_create(user=request.user)
    
     
        


#     # ////

#     if 'cart_data_obj' in request.session:
#         if str(request.GET['id']) in request.session['cart_data_obj']:
#             cart_data = request.session['cart_data_obj']
#             cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
#             cart_data.update(cart_data)
#             request.session['cart_data_obj'] = cart_data
#         else:
#             cart_data = request.session['cart_data_obj']
#             cart_data.update(cart_product)
#             request.session['cart_data_obj'] = cart_data

#     else:
#         request.session['cart_data_obj'] = cart_product
#     return JsonResponse({"data":request.session['cart_data_obj'], 'totalCartItems':len(request.session['cart_data_obj'])})



# def cart_view(request):
#     context = {}
#     if 'cart_data_obj' in request.session:
#         cart_total_amount = 0
#         cart_data = request.session['cart_data_obj']
#         for pid, item in cart_data.items():
#             product_variant = ProductVariant.objects.get(id=pid)
#             cart_total_amount += int(item['qty']) * float(item['price'])
#             item['stock'] = product_variant.stock
        

#         context = {
#             "cart_data": cart_data,
#             'totalCartItems': len(cart_data),
#             'cart_total_amount': cart_total_amount,
#         }
#     else:
#         messages.warning(request, "Your cart is empty")
#         return redirect("product:index")

#     return render(request, "user/cart.html", context)



# def delete_item_from_cart(request):
#     product_id = str(request.GET['id'])

#     if 'cart_data_obj' in request.session:
#         if product_id in request.session['cart_data_obj']:
#             cart_data = request.session['cart_data_obj']
#             del request.session['cart_data_obj'][product_id]
#             request.session['cart_data_obj'] = cart_data

#     cart_total_amount = 0
#     if 'cart_data_obj' in request.session:
#         for pid, item in request.session['cart_data_obj'].items():
#             cart_total_amount += int(item['qty']) * float(item['price'])


#     context = render_to_string("user/async/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalCartItems':len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
#     return JsonResponse({"data": context, 'totalCartItems':len(request.session['cart_data_obj']), })



# def update_cart(request):
#     product_id = str(request.GET['id'])
#     product_qty = request.GET['qty']
#     print(f'hellooi {product_qty}')

#     if 'cart_data_obj' in request.session:
#         if product_id in request.session['cart_data_obj']:
#             cart_data = request.session['cart_data_obj']
#             cart_data[str(request.GET['id'])]['qty'] = product_qty
#             request.session['cart_data_obj'] = cart_data

#     cart_total_amount = 0
#     if 'cart_data_obj' in request.session:
#         for pid, item in request.session['cart_data_obj'].items():
#             cart_total_amount += int(item['qty']) * float(item['price'])


#     context = render_to_string("user/async/cart.html", {"cart_data":request.session['cart_data_obj'], 'totalCartItems':len(request.session['cart_data_obj']), 'cart_total_amount':cart_total_amount})
#     return JsonResponse({"data": context, 'totalCartItems':len(request.session['cart_data_obj']), })










