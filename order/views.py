from django.conf import settings
import uuid
from django.http import Http404, JsonResponse
from django.shortcuts import  get_object_or_404, render, redirect
from django.contrib import messages
from product.models import User
from cart.models import Cart_Item,Cart
from account.models import Address
from django.db.models import Q
from decimal import Decimal
from ad_product.models import ProductVariant
from order.models import Order,OrderItem,Payment
from account.models import UserProfile
from django.views.decorators.cache import cache_control
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required



# Create your views here.

def order_view(request):
    cart = Cart.objects.get(user = request.user)
    cart_item = Cart_Item.objects.filter(cart = cart.id)
    myuser =request.user
    print(myuser)
    default_billing = None  
    default_shipping = None
    billing_address = None
    shipping_address = None
    try:
        default_shipping = Address.objects.filter(Q(is_shipping = True) & Q(is_default = True) & Q( user = request.user))
        default_billing = Address.objects.filter(Q(is_billing = True) & Q(is_default = True) & Q( user = request.user))
        billing_address = Address.objects.filter(Q(is_billing = True) & Q(is_default = False) & Q( user = request.user))
        shipping_address = Address.objects.filter(Q(is_shipping = True) & Q(is_default = False) & Q( user = request.user))
        print(f' the shipping address{shipping_address}')
        print(f'the billing address{billing_address}')
        print(f'the default shipping address{default_shipping}')
        print(f'the default billing address{default_billing}')
    except Exception as e:
        print(f'the error {e}')
    context = {
        'cart' : cart,  
        'cart_item': cart_item,
        'default_billing' :default_billing if default_billing else None ,
        'default_shipping' :default_shipping if default_shipping else None,
        'billing_address':billing_address if billing_address else None,
        'shipping_address':shipping_address if shipping_address else None,
    }
    return render(request, 'user/checkout.html',context)



@login_required
def place_order(request):
    context = {} 

    if request.method == 'POST':

        shipping_address_id = request.POST.get('shipping_add')
        billing_address_id = request.POST.get('billing_add')
        

        try:
            shipping = Address.objects.get(id=shipping_address_id)
            billing = Address.objects.get(id=billing_address_id)
        except (Address.DoesNotExist, ValueError):
            messages.warning(request, 'No address selected')
            print('not working')
            return redirect('order:order_view')
        cart = Cart.objects.get(user = request.user)
        cart_item = Cart_Item.objects.filter(cart = cart)

        if cart_item.exists():
            payment_maker = Payment.objects.create(
            user=request.user,
            payment_method = "COD",
            payment_status = 'PENDING',
            amount_paid = cart.total,
            )
            try:
                new_order =Order.objects.create(
                user=request.user,
                payment_details = payment_maker,
                shipping_address = shipping,
                billing_address = billing,
                order_total = cart.total ,
                order_subtotal = cart.sub_total,
                order_shipping = cart.shipping,
                )
                request.session['new_order'] = new_order.pk
                cart.save()

            except Exception as e:
                print(f' the error {e}')

        for cart_item in cart_item:
            product = ProductVariant.objects.get(id=cart_item.product.id)
            uu_order_id = int(uuid.uuid4().hex[:8],16)
            uu_order_id = f"#{uu_order_id}"

            order_item, _ = OrderItem.objects.get_or_create(
                user=request.user, 
                order_product=product,
                order_item_id = uu_order_id,
                quantity=cart_item.quantity, 
                product_price=cart_item.product.sale_price, 
                payment_details=payment_maker,
                order = new_order,
                order_status = 'PROCESSING',
                )
            
            product.stock -= cart_item.quantity
            product.save()
            order_item.save()
            cart_item.delete()

        new_order = None  # Default value if new_order is not defined
        order_items = []
        last_order = Order.objects.latest('order_time')
                
        if last_order:
            last_order_id = last_order.order_number
        else:
            last_order_id = None 
        new_order_id = request.session.get('new_order')
        order_id = new_order_id
        if order_id:
            new_order = Order.objects.get(pk=order_id)
            order_items = OrderItem.objects.filter(order=new_order)
        else:
            new_order = Order.objects.get(pk=last_order_id)
            order_items = OrderItem.objects.filter(order=new_order)
            
        context = {
        'new_order': new_order,
        'order_items': order_items,
        }
        
        
        return render(request, 'user/order_summary.html', context)
    




def cancel_order_req(request,id):
    print(f' ndfk the error {id}')
    item = OrderItem.objects.get(pk= id)

    context = {
        "item" : item   
    }
    return render(request, 'user/order/order_cancel_reason.html',context)
    


def cancel_order(request,id):

    order_item = OrderItem.objects.get(id = id)
    Product = ProductVariant.objects.get(id = order_item.order_product.id)
    user_details = get_object_or_404(UserProfile, user = request.user)
    order = Order.objects.get(pk = order_item.order.pk)
    finder = OrderItem.objects.filter(order = order)
    amount = None

    if request.method =="POST":

        try:

            reason = request.POST['reason']
            if reason is None:
                messages.warning(request,'Reason for cancellation is Must')

            order_item.cancel_reason = reason
            order_item.order_status = 'CANCELLED'
            Product.stock += int(order_item.quantity)
            amount = (int(order_item.product_price) * int(order_item.quantity))
            order_item.order.order_total -= amount
            order_item.order.save()
            order_item.save()

            if len(finder) <= 1:
                order_item.order.order_total = 0
                order_item.order.save()

                
            Product.save()

            context = {
                'order_item':order_item,
                'profile':user_details, 
                'Product':Product,
            }
           
            
            return redirect('order:view-orders', order_item.order.pk)
        
        except Exception as e:
            return redirect('order:view-orders')
        
    return render(request, 'user/order/order_cancel.html')






@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required()
def user_orders(request, id ):
    order = get_object_or_404(Order, pk=id)
    order_item = OrderItem.objects.filter(order=order)
    context = {
        "order_item":order_item,
    }
    return render(request, 'user/dashboard/order-detail.html',context)

    



def order_details(request):

    shipping=None
    billing=None
    order_item=None
    order=None
    user_details=None

    try:

        new_order = request.session.get('new_order')

        order = Order.objects.get_ob(order_number = new_order)
        order_item = OrderItem.objects.filter(order = order)
        user_details = UserProfile.objects.get(user = request.user)
        shipping = Address.objects.get(id=order.shipping_address.id)
        billing = Address.objects.get(id=order.billing_address.id)

    except Exception as e:
        print(f'the error is in {e}')

    context = {
        'order_item':order_item,
        'order':order,
        'profile':user_details,
        'billing':billing,
        'shipping':shipping,
    }
    messages.success(request, 'Hooray the order have been placed')

    return render(request, 'user/order-detail.html',context)




def order_listing(request,id):  
    order = Order.objects.get(order_number = id)
    order_item = OrderItem.objects.filter(order = order)
    user_details = UserProfile.objects.get(user = request.user)

    print(f"the order item {order_item}")
    context = {
        'order':order,
        'order_item':order_item,
        'profile':user_details,
    }

    return render(request, 'user/order/order_item_listing_user.html',context)






def admin_order_view(request):
    order = Order.objects.all().order_by('-order_time')

    context ={
        'order':order,
    }
    return render(request, 'admin/order/orders.html',context)


def admin_order_item_view(request, id):
    order = Order.objects.get(order_number=id)
    order_item = OrderItem.objects.filter(order=order)
    
    context={
        'order_item':order_item,
        'order':order
    }

    return render(request, 'admin/order/order_item_view.html',context)



def admin_order_item_details(request, id):
    order_no = id
    order_item = OrderItem.objects.get(id=order_no)

    print(order_item)
    context={
        'order_item':order_item,
    }
    return render(request, 'admin/dashboard/order/order_item_details.html',context)

def admin_order_status(request):
    order_id = None

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':

        try:

            order_id = request.POST.get('order_id')
            select_status = request.POST.get('status')
            order_item = get_object_or_404(OrderItem, order_item_id = order_id)
            order_item.order_status = select_status

            if select_status == "CANCELLED":
                order_item.order.order_total -= (int(order_item.product_price) * int(order_item.quantity))

                if order_item.order.order_total < 0:
                    order_item.order.order_total = 0

                order_item.order.save()
            order_item.save()
            data = {'success': True}
            return JsonResponse(data)
        
        except Exception as e:
            print(f'order change: {e}')
            data = {'success': False}
            return JsonResponse(data)

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def admin_order_status_all(request):
    order_id = None
    order = None
    select_status = None

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':

        try:

            order_id = request.POST.get('order_id')
            select_status = request.POST.get('status')
            order = get_object_or_404(Order, order_number=order_id)
            order_item = OrderItem.objects.filter(Q(order=order) & ~Q(order_status='CANCELLED') & ~Q(order_status = 'DELIVERED') & ~Q(order_status = 'RETURNED'))
            for item in order_item:
                item.order_status = select_status

                if select_status == 'CANCELLED':
                    order.order_total -= (int(item.product_price) * int(item.quantity))

                order.save()
                item.save()

                if order.order_total < 0:
                    order.order_total = 0
                    order.save()

                print('inside the all cancel ) setting if')
                messages.info(request, f'The order Number {order_id} status has been changed')
            data = {'success': True}
            return JsonResponse(data)
        except Exception as e:

            print(f'The error is in admin all order change: {e}')
            data = {'success': False}
            return JsonResponse(data)
    return JsonResponse({'success': False, 'error': 'Invalid request'})







def user_details_views(request,id):

    user = get_object_or_404(User, id=id)
    order = None
    shipping = None
    billing = None

    try:
        # order = Order.objects.filter(user = user).count()
        shipping = Address.objects.get(Q(user = user) & Q(is_shipping=True) & Q(is_default=True))
        billing= Address.objects.get(Q(user = user) & Q(is_billing=True) & Q(is_default=True))

    except Exception as e:
        print(e)

    context = {

        'user' :user,
        'user_profile':UserProfile.objects.get(user = user),
        'billing': billing if billing else Address.objects.filter(Q(user = user) & Q(is_billing=True)).first(),
        'shipping': shipping if shipping else Address.objects.filter(Q(user = user) & Q(is_shipping=True)).first(),
        'order_count':order,
    }

    return render(request, 'admin/dashboard/order/admin_user_view.html',context)






# def order_placed_view(request):
#     new_order = request.session.get('new_order')
#     user_details = UserProfile.objects.get(user = request.user)
#     my_new_order = Order.objects.get(pk = new_order)
#     context = {
#     'order_item':OrderItem.objects.filter(order = my_new_order.pk),   
#     'order':my_new_order,
#     'profile':user_details,
#     'billing':my_new_order.shipping_address,
#     'shipping':my_new_order.billing_address,
#     }
  
#     return render(request, 'user/order_placed_view.html', context)


