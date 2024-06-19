from django.conf import settings
import uuid
import razorpay
from django.http import Http404, JsonResponse
from django.shortcuts import  get_object_or_404, render, redirect
from django.contrib import messages
from product.models import User
from cart.models import Cart_Item,Cart, Coupon
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
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from wallet.models import *
from wallet.views import credit, easypay
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from django.utils.dateparse import parse_date


# Create your views here.

def order_view(request):
    
    cart = Cart.objects.get(user = request.user)
    cart_items = Cart_Item.objects.filter(cart = cart.id)
    dis = 0
    for cart_item in cart_items:
        if cart_item.product.stock < cart_item.quantity:
            messages.warning(request, "The product doesn't have that many quantities available.")
            return redirect('cart:view_cart')
    
    
    myuser =request.user
    default_billing = None  
    default_shipping = None
    billing_address = None
    shipping_address = None
    try:
        default_shipping = Address.objects.filter(Q(is_shipping = True) & Q(is_default = True) & Q( user = request.user))
        default_billing = Address.objects.filter(Q(is_billing = True) & Q(is_default = True) & Q( user = request.user))
        billing_address = Address.objects.filter(Q(is_billing = True) & Q(is_default = False) & Q( user = request.user))
        shipping_address = Address.objects.filter(Q(is_shipping = True) & Q(is_default = False) & Q( user = request.user))
        
    except Exception as e:
        print(f'exception = {e}')
    context = {
        'cart' : cart,  
        'dis' : dis,  
        'cart_items': cart_items,
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

        if 'cod' in request.POST:
            shipping_address_id = request.POST.get('shipping_add')
            billing_address_id = request.POST.get('billing_add')
            

            try:
                shipping = Address.objects.get(id=shipping_address_id)
                billing = Address.objects.get(id=billing_address_id)
            except (Address.DoesNotExist, ValueError):
                messages.warning(request, 'No address selected')
                print('not working')
                return redirect('order:order_view')
            
            shipping_full_address = shipping.FullAddress()
            billing_full_address = billing.FullAddress()
            print(shipping_full_address)
            print(billing_full_address)

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
                    shipping_address = shipping_full_address,
                    billing_address = billing_full_address,
                    order_total = cart.total ,
                    order_subtotal = cart.sub_total,
                    order_shipping = cart.shipping,
                    )
                    if 'coupon' in request.session:
                        coupon = request.session.get('coupon')
                        coupon = Coupon.objects.get(pk = coupon)
                        new_order.order_coupon = coupon
                        new_order.save()
                        coupon_discount = cart.total * coupon.discount /100
                        if coupon_discount > coupon.max_discount_amount:
                            coupon_discount = coupon.max_discount_amount
                    else:
                        coupon_discount = 0
                    request.session['new_order'] = new_order.pk
                    cart.save()

                except Exception as e:
                    print(f' the error {e}')

            for cart_item in cart_item:
                product = ProductVariant.objects.get(id=cart_item.product.id)
                uu_order_id = int(uuid.uuid4().hex[:8],16)
                uu_order_id = f"#{uu_order_id}"
                total_product_price = cart_item.product.sale_price * cart_item.quantity

                order_item, _ = OrderItem.objects.get_or_create(
                    user=request.user, 
                    order_product=product,
                    order_item_id = uu_order_id,
                    quantity=cart_item.quantity, 
                    product_price=total_product_price, 
                    payment_details=payment_maker,
                    order = new_order,
                    order_status = 'PLACED',
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
            'coupon_discount': coupon_discount
            }
            
            return render(request, 'user/order_summary.html', context)
        
        
            
        
        elif 'coupon_submit' in request.POST:
            last_order = Order.objects.latest('order_time')
            code = request.POST.get("user_coupon")
            coupon = Coupon.objects.filter(code=code, is_active=True).first()
            cart = Cart.objects.get(user = request.user)
            cart_item = Cart_Item.objects.filter(cart = cart)
            if coupon:
                if cart.coupon and coupon == cart.coupon:
                    messages.warning(request, 'Coupon already applied')
                    return redirect("order:order_view")
                else:

                    discount = cart.total * coupon.discount /100
                    cart.coupon = coupon

                    if discount > coupon.max_discount_amount:
                        discount = coupon.max_discount_amount
                    cart.total = cart.sub_total + cart.shipping
                    cart.total -= discount
                    print(f'discount={discount}')

                    request.session['coupon'] = coupon.pk

                    cart.save()
                    messages.success(request,'Coupon applied')
                    return redirect("order:order_view")
            else:
                messages.warning(request, "Coupon does'nt exist")
                return redirect("order:order_view")
            

        # elif 'wallet_pay' in request.POST:
        #     shipping_address_id = request.POST.get('shipping_add')
        #     billing_address_id = request.POST.get('billing_add')

        #     try:
        #         shipping = Address.objects.get(id=shipping_address_id)
        #         billing = Address.objects.get(id=billing_address_id)
        #     except (Address.DoesNotExist, ValueError):
        #         messages.warning(request, 'No address selected')
        #         print('not working')
        #         return redirect('order:order_view')

        #     shipping_full_address = shipping.FullAddress()
        #     billing_full_address = billing.FullAddress()

        #     cart = Cart.objects.get(user=request.user)
        #     cart_item = Cart_Item.objects.filter(cart=cart)

        #     # Check wallet balance before proceeding
        #     user_wallet = EasyPay.objects.get(user=request.user)
        #     if cart.total <= user_wallet.balance:
        #         payment_maker = Payment.objects.create(
        #             user=request.user,
        #             payment_method="Wallet",
        #             payment_status='SUCCESS',
        #             amount_paid=cart.total,
        #         )
        #         try:
        #             new_order = Order.objects.create(
        #                 user=request.user,
        #                 payment_details=payment_maker,
        #                 shipping_address=shipping_full_address,
        #                 billing_address=billing_full_address,
        #                 order_total=cart.total,
        #                 order_subtotal=cart.sub_total,
        #                 order_shipping=cart.shipping,
        #             )
        #             # ... rest of your order creation logic using new_order (similar to COD)

        #             # Update wallet balance after successful order creation
        #             user_wallet.balance -= cart.total
        #             user_wallet.save()

        #             # ... rest of your success logic

        #         except Exception as e:
        #             print(f' the error {e}')
        #     else:
        #         messages.warning(request, 'Insufficient funds in wallet')
        #         return redirect('order:order_view')


            

        elif 'order_pay' in request.POST:
            shipping_address_id = request.POST.get('shipping_add')
            billing_address_id = request.POST.get('billing_add')
            

            try:
                shipping = Address.objects.get(id=shipping_address_id)
                billing = Address.objects.get(id=billing_address_id)
            except (Address.DoesNotExist, ValueError):
                messages.warning(request, 'No address selected')
                print('not working')
                return redirect('order:order_view')
            
            shipping_full_address = shipping.FullAddress()
            billing_full_address = billing.FullAddress()
            print(shipping_full_address)
            print(billing_full_address)

            cart = Cart.objects.get(user = request.user)
            cart_item = Cart_Item.objects.filter(cart = cart)

            

            

            if cart_item.exists():
                payment_maker = Payment.objects.create(
                user=request.user,
                payment_method = "RazorPay",
                payment_status = 'PENDING',
                amount_paid = cart.total,
                )
                try:
                    new_order =Order.objects.create(
                    user=request.user,
                    payment_details = payment_maker,
                    shipping_address = shipping_full_address,
                    billing_address = billing_full_address,
                    order_total = cart.total ,
                    order_subtotal = cart.sub_total,
                    order_shipping = cart.shipping,
                    )
                    if 'coupon' in request.session:
                        print('hi')
                        coupon = request.session.get('coupon')
                        print(f'coupon = {coupon}')
                        coupon = Coupon.objects.get(pk = coupon)
                        new_order.order_coupon = coupon
                        new_order.save()
                        coupon_discount = cart.total * coupon.discount /100
                        if coupon_discount > coupon.max_discount_amount:
                            coupon_discount = coupon.max_discount_amount
                    else:
                        coupon_discount = 0
                    request.session['new_order'] = new_order.pk
                    cart.save()

                

                except Exception as e:
                    print(f' the error {e}')

            for cart_item in cart_item:
                product = ProductVariant.objects.get(id=cart_item.product.id)
                uu_order_id = int(uuid.uuid4().hex[:8],16)
                uu_order_id = f"#{uu_order_id}"
                total_product_price = cart_item.product.sale_price * cart_item.quantity

                order_item, _ = OrderItem.objects.get_or_create(
                    user=request.user, 
                    order_product=product,
                    order_item_id = uu_order_id,
                    quantity=cart_item.quantity, 
                    product_price=total_product_price, 
                    payment_details=payment_maker,
                    order = new_order,
                    order_status = 'PLACED',
                    )
            
                order_item.save()
                # cart_item.delete()

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


            order_total = new_order.order_total
            

            request.session['new_order_id'] = new_order.pk
            request.session['payment_maker_id'] = payment_maker.pk
            request.session['cart_id'] = cart.pk

            print(f'p = {payment_maker.pk}')
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
                payment = client.order.create({ "amount": int(order_total), "currency": "INR"})
            except:
                payment = False

            print(f'payment = {payment}')
            success_page_url = request.build_absolute_uri(reverse('order:success'))
            failed_page_url = request.build_absolute_uri(reverse('order:failed'))
            context = {
            'new_order': new_order,
            'order_items': order_items,
            'payment': payment,
            'success_page_url': success_page_url,
            'success': success_page_url,
            'failed': failed_page_url,
            'coupon_discount': coupon_discount,
            }
            
            print("fi")
            return render(request, 'user/order_summary.html', context)
    # return redirect("order:failed")
    



def payment_success(request):
   
    order_id = request.session.get('new_order_id')
    payment_maker_id = request.session.get('payment_maker_id')
    cart_id = request.session.get('cart_id')
    payment_sign = request.GET.get('payment_sign')
    payment_id = request.GET.get('payment_id')


    cart = Cart.objects.get(id = cart_id)
    
    order = Order.objects.get(pk = order_id)
    payment_maker = Payment.objects.get(id=payment_maker_id)

    order_items = OrderItem.objects.filter(order = order)

    for items in order_items:
        items.order_status = "PROCESSING"
        product = ProductVariant.objects.get(id = items.order_product.pk)
        product.stock -= items.quantity
        product.save()
        items.save()
    payment_maker.payment_status = 'SUCCESS'
    payment_maker.payment_signature = payment_sign
    payment_maker.razorpay_payment_id = payment_id
    
    
    cart.delete()
    payment_maker.save()
    messages.success(request,'Order placed and payment successfull')
    return redirect('product:index')

         

def payment_failed(request):

    order_id = request.session.get('new_order_id')
    payment_maker_id = request.session.get('payment_maker_id')
    cart_id = request.session.get('cart_id')

    
    order = Order.objects.get(pk = order_id)
    payment_maker = Payment.objects.get(id=payment_maker_id)

    order_items = OrderItem.objects.filter(order = order)

    

    for items in order_items:
        items.order_status = "CANCELLED"
        
        items.save()
    payment_maker.payment_status = 'FAILED'

    payment_maker.save()
    messages.success(request,'payment failed')
    return redirect('order:order_view')



def invoice_download(request):
    
    ...




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
            if order.order_coupon:
                order_item_count = order.orderitem_set.count()
                coupon = order.order_coupon.pk
                coupon = Coupon.objects.get(pk = coupon)
                discount = (order.order_subtotal + order.order_shipping) * coupon.discount /100

                if discount > coupon.max_discount_amount:
                    discount = coupon.max_discount_amount

                disc_div = discount / order_item_count
                
                amount = order_item.product_price - disc_div
                order_item.order.order_total -= amount
                order_item.order.save()
                order_item.save()  


            else:
                amount = (int(order_item.product_price) * int(order_item.quantity))
                order_item.order.order_total -= amount
                order_item.order.save()
                order_item.save()  
            

            if order.payment_details.payment_status == 'SUCCESS':
                easypay = EasyPay.objects.get(user = request.user)
                easypay.balance += amount
                easypay.save()

                order.payment_details.payment_status = "REFUNDED"
                order.payment_details.save()
                order.save()

                user = request.user

                credit(amount, order_item, user)
                messages.success(request,' Order Cancelled and Amount has been refunded ')

               
            if len(finder) <= 1:
                order_item.order.order_total = 0
                # order_item.order.save()

                
            # Product.save()

            context = {
                'order_item':order_item,
                'profile':user_details, 
                'Product':Product,
            }
           
            
            return redirect('order:view-orders', order_item.order.pk)
        
        except Exception as e:
            return redirect('order:view-orders')
        
    return render(request, 'user/order/order_cancel.html')



def return_order_req(request,id):
    print(f' ndfk the error {id}')
    item = OrderItem.objects.get(pk= id)

    context = {
        "item" : item   
    }
    return render(request, 'user/order/order_return_reason.html',context)


def return_order(request,id):

    order_item = OrderItem.objects.get(id = id)
    Product = ProductVariant.objects.get(id = order_item.order_product.id)
    user_details = get_object_or_404(UserProfile, user = request.user)
    order = Order.objects.get(pk = order_item.order.pk)
    finder = OrderItem.objects.filter(order = order)
    wallet = Wallet.objects.get(user = request.user)
    amount = None

    if request.method =="POST":

        try:

            reason = request.POST['reason']
            if reason is None:
                messages.warning(request,'Reason for cancellation is Must')

            order_item.cancel_reason = reason
            order_item.order_status = 'RETURNED'
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
        
    return render(request, 'user/order/order_return.html')




@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required()
def user_orders(request, id ):
    order = get_object_or_404(Order, pk=id)
    order_item = OrderItem.objects.filter(order=order)
    order_item_queryset = OrderItem.objects.filter(order=order)
    if order_item_queryset.exists():  # Check if any order items exist
        order_ite = order_item_queryset.first()  # Get the first order item
        if order_ite.order_status == "DELIVERED":
         order_ite.payment_details.payment_status = 'SUCCESS'  # Access the payment_details attribute
    discount = order.get_actual_discount()

    context = {
        "order_item":order_item,
        "order":order,
        "discount" : discount
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

        order = Order.objects.get(order_number = new_order)
        order_item = OrderItem.objects.filter(order = order)
        user_details = UserProfile.objects.get(user = request.user)
        shipping = Address.objects.get(id=order.shipping_address.id)
        billing = Address.objects.get(id=order.billing_address.id)

        for o in order_item:
            order_no = o.order.order_number
        print(f'or = {order_item}')
    except Exception as e:
        print(f'the error is in {e}')

    context = {
        'order_item':order_item,
        'order':order,
        'order_no':order_no,
        'profile':user_details,
        'billing':billing,
        'shipping':shipping,
    }
    messages.success(request, 'Hooray the order have been placed')

    return render(request, 'user/order-detail.html',context)



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def download_invoice(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_item = OrderItem.objects.filter(order=order)
        user_details = UserProfile.objects.get(user=request.user)
        shipping = order.shipping_address
        billing = order.billing_address
        total = 0
        for i in order_item:
            total += i.product_price
        discount = total - order.order_total
        context = {
            'order_item': order_item,
            'order': order,
            'profile': user_details,
            'billing': billing,
            'shipping': shipping,
            'discount':discount,
            'total':total,
        }

        pdf = render_to_pdf('user/order/invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f"Invoice_{order.order_number}.pdf"
            content = f"inline; filename={filename}"
            download = request.GET.get("download")
            if download:
                content = f"attachment; filename={filename}"
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

    except Exception as e:
        return HttpResponse(f"Error generating PDF: {e}")




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


def filter_orders_by_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        orders = Order.objects.filter(order_time__range=[start_date, end_date]).order_by('-order_time')
    else:
        orders = Order.objects.all().order_by('-order_time')

    orders_data = [
        {
            'order_number': order.order_number,
            'username': order.user.username if order.user else 'N/A',
            'email': order.user.email if order.user else 'N/A',
            'order_subtotal': order.order_subtotal,
            'payment_status': order.payment_details.payment_status if order.payment_details else 'N/A',
            'order_time': order.order_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        for order in orders
    ]

    return JsonResponse({'orders': orders_data})



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


