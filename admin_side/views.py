from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.contrib.auth import authenticate,logout,login
from django.http import HttpResponseRedirect
from userauths.models import User
from django.urls import reverse
from .forms import CouponForm
from cart.models import Coupon
from order.models import Order,OrderItem,Payment
from django.db.models import Sum, F
from ad_product.models import Product, ProductVariant
from category_manage.models import Category
from django.utils import timezone
from datetime import timedelta,datetime
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeekDay
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa



def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

def download_sales_report(request):
    # Retrieve data for the sales report
    total_sales = Order.objects.aggregate(total_sales=Sum('order_total'))['total_sales']
    total_shipping = Order.objects.aggregate(total_shipping=Sum('order_shipping'))['total_shipping']
    total_sales_amount = total_sales - total_shipping

    no_of_order = Order.objects.count()

    no_of_products = Product.objects.count()
    no_of_varients = ProductVariant.objects.count()
    no_of_categories = Category.objects.count()

    today = timezone.now().date()
    new_users = User.objects.filter(date_joined__date=today)

    now = timezone.now()
    monthly_orders = Order.objects.filter(order_time__year=now.year, order_time__month=now.month)
    total_order_amount = monthly_orders.aggregate(total_earnings=Sum('order_total'))['total_earnings']
    total_shipping_cost = monthly_orders.aggregate(total_shipping=Sum('order_shipping'))['total_shipping']
    total_order_amount = total_order_amount if total_order_amount is not None else 0
    total_shipping_cost = total_shipping_cost if total_shipping_cost is not None else 0
    monthly_earnings = total_order_amount - total_shipping_cost

    overall_subtotal = Order.objects.aggregate(overall_subtotal=Sum('order_subtotal'))['overall_subtotal']
    overall_discount = overall_subtotal - total_sales
    
    weekly_sales_data = get_weekly_sales()  # Assuming this function is defined elsewhere
    monthly_sales_data = get_monthly_sales()  # Assuming this function is defined elsewhere
    yearly_sales_data = get_yearly_sales()  # Assuming this function is defined elsewhere
    
    weekly_sales_str = ",".join(map(str, weekly_sales_data))
    monthly_sales_str = ",".join(map(str, monthly_sales_data))
    yearly_sales_str = ",".join(map(str, yearly_sales_data))

    # Define the data to be passed to the template
    data = {
        'user': request.user,
        'overall_sales': total_sales_amount,
        'orders': no_of_order,
        'products': no_of_products,
        'varients': no_of_varients,
        'categ': no_of_categories,
        'new_users': new_users.count(),
        'monthly_earnings': monthly_earnings,
        'discount': overall_discount,
        'weekly_sales_data': weekly_sales_str,
        'monthly_sales_data': monthly_sales_str,
        'yearly_sales_data': yearly_sales_str,
    }

    # Render the template to PDF
    pdf_data = render_to_pdf('admin/dashboard_pdf_template.html', data)
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)


@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def superuser_login(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_side:dashboard')  # Redirect to dashboard or any desired page
        else:
            # Add error message for invalid login attempt
            error_message = "Invalid username or password"
            return render(request, 'admin/admin_login.html', {'error_message': error_message})
    return render(request, 'admin/admin_login.html')



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required
def dashboard(request):

    # Calculate total sales
    total_sales = Order.objects.aggregate(total_sales=Sum('order_total'))['total_sales']
    total_shipping = Order.objects.aggregate(total_shipping=Sum('order_shipping'))['total_shipping']
    total_sales_amount = total_sales - total_shipping

    # Count total orders
    no_of_order = Order.objects.count()

    # Count products, variants, and categories
    no_of_products = Product.objects.count()
    no_of_varients = ProductVariant.objects.count()
    no_of_categories = Category.objects.count()

    # Filter new users for today
    today = timezone.now().date()
    new_users = User.objects.filter(date_joined__date=today)

     # Calculate monthly earnings
    now = timezone.now()
    monthly_orders = Order.objects.filter(order_time__year=now.year, order_time__month=now.month)
    total_order_amount = monthly_orders.aggregate(total_earnings=Sum('order_total'))['total_earnings']
    total_shipping_cost = monthly_orders.aggregate(total_shipping=Sum('order_shipping'))['total_shipping']
    total_order_amount = total_order_amount if total_order_amount is not None else 0
    total_shipping_cost = total_shipping_cost if total_shipping_cost is not None else 0
    monthly_earnings = total_order_amount - total_shipping_cost

    # Calculate overall discount
    overall_subtotal = Order.objects.aggregate(overall_subtotal=Sum('order_subtotal'))['overall_subtotal']
    overall_discount = overall_subtotal - total_sales
    
    # Get weekly, monthly, and yearly sales data
    weekly_sales_data = get_weekly_sales()
    monthly_sales_data = get_monthly_sales()
    yearly_sales_data = get_yearly_sales()
    weekly_sales_str = ",".join(map(str, weekly_sales_data))
    monthly_sales_str = ",".join(map(str, monthly_sales_data))
    yearly_sales_str = ",".join(map(str, yearly_sales_data))

    # Calculate total coupon deduction
    orders = Order.objects.all()
    total_coupon_deduction = sum(order.get_actual_discount() for order in orders)

    # Get top 10 selling products
    top_selling_products = (OrderItem.objects
                            .values(product_name=F('order_product__product__product_name'),
                                    product_img=F('order_product__product__product_img'),
                                    product_catg=F('order_product__product__product_catg__category_name'),
                                    created_at=F('order_product__product__created_at'),
                                    stock_count=F('order_product__stock'),
                                    product_status=F('order_product__product_status'),
                                    is_active=F('order_product__is_active'))
                            .annotate(total_quantity=Sum('quantity'))
                            .order_by('-total_quantity')[:10])
    
    # Get top 2 selling categories


    top_selling_categories = (OrderItem.objects
                            .values(category_name=F('order_product__product__product_catg__category_name'),
                                    category_img=F('order_product__product__product_catg__category_img'))
                            .annotate(total_quantity=Sum('quantity'))
                            .order_by('-total_quantity')[:2])



    
    




    context = {
        'user': request.user,
        'overall_sales':total_sales_amount,
        'orders':no_of_order,
        'products':no_of_products,
        'varients':no_of_varients,
        'categ':no_of_categories,
        'new_users':new_users,
        'monthly_earnings':monthly_earnings,
        'discount':overall_discount,
        'weekly_sales_data': weekly_sales_str,
        'monthly_sales_data': monthly_sales_str,
        'yearly_sales_data': yearly_sales_str,
        'coupon_deduction': total_coupon_deduction,
        'top_selling_products':top_selling_products,
        'top_selling_categories':top_selling_categories,
    }
    return render(request, 'admin/dashboard.html', context)


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=result)
    if not pdf.err:
        return result.getvalue()
    return None

def download_sales_report(request):
    # Retrieve data for the sales report
    total_sales = Order.objects.aggregate(total_sales=Sum('order_total'))['total_sales']
    total_shipping = Order.objects.aggregate(total_shipping=Sum('order_shipping'))['total_shipping']
    total_sales_amount = total_sales - total_shipping

    no_of_order = Order.objects.count()

    no_of_products = Product.objects.count()
    no_of_varients = ProductVariant.objects.count()
    no_of_categories = Category.objects.count()

    today = timezone.now().date()
    new_users = User.objects.filter(date_joined__date=today)

    now = timezone.now()
    monthly_orders = Order.objects.filter(order_time__year=now.year, order_time__month=now.month)
    total_order_amount = monthly_orders.aggregate(total_earnings=Sum('order_total'))['total_earnings']
    total_shipping_cost = monthly_orders.aggregate(total_shipping=Sum('order_shipping'))['total_shipping']
    total_order_amount = total_order_amount if total_order_amount is not None else 0
    total_shipping_cost = total_shipping_cost if total_shipping_cost is not None else 0
    monthly_earnings = total_order_amount - total_shipping_cost

    overall_subtotal = Order.objects.aggregate(overall_subtotal=Sum('order_subtotal'))['overall_subtotal']
    overall_discount = overall_subtotal - total_sales
    
    weekly_sales_data = get_weekly_sales()  # Assuming this function is defined elsewhere
    monthly_sales_data = get_monthly_sales()  # Assuming this function is defined elsewhere
    yearly_sales_data = get_yearly_sales()  # Assuming this function is defined elsewhere
    
    weekly_sales_str = ",".join(map(str, weekly_sales_data))
    monthly_sales_str = ",".join(map(str, monthly_sales_data))
    yearly_sales_str = ",".join(map(str, yearly_sales_data))

    # Define the data to be passed to the template
    data = {
        'user': request.user,
        'overall_sales': total_sales_amount,
        'orders': no_of_order,
        'products': no_of_products,
        'varients': no_of_varients,
        'categ': no_of_categories,
        'new_users': new_users.count(),
        'monthly_earnings': monthly_earnings,
        'discount': overall_discount,
        'weekly_sales_data': weekly_sales_str,
        'monthly_sales_data': monthly_sales_str,
        'yearly_sales_data': yearly_sales_str,
    }

    # Render the template to PDF
    pdf_data = render_to_pdf('admin/dashboard_pdf_template.html', data)
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=400)



def get_monthly_sales():
    # Query to get monthly sales for the current year
    monthly_sales = Payment.objects.filter(
        payment_time__year=timezone.now().year,
        payment_status="SUCCESS"
    ).annotate(month=ExtractMonth('payment_time')).values('month').annotate(monthly_total=Sum('amount_paid')).order_by('month')

    monthly_sales_values = [0] * 12
    print(monthly_sales)
    for entry in monthly_sales:
        month_index = entry['month'] - 1
        monthly_sales_values[month_index] = entry['monthly_total']

    return monthly_sales_values


def get_yearly_sales():
    # Get the current year
    current_year = timezone.now().year
    
    # Get the last few years (you can adjust the range as needed)
    start_year = current_year - 2  # For example, the last three years
    
    # Filter payments for the last few years and with status "SUCCESS"
    yearly_sales = Payment.objects.filter(
        payment_time__year__gte=start_year,
        payment_status="SUCCESS"
    ).annotate(year=ExtractYear('payment_time')).values('year').annotate(yearly_total=Sum('amount_paid')).order_by('year')

    # Create a dictionary to hold the yearly sales
    yearly_sales_dict = {year: 0 for year in range(start_year, current_year + 1)}
    
    for entry in yearly_sales:
        yearly_sales_dict[entry['year']] = entry['yearly_total']

    # Convert the dictionary values to a list
    yearly_sales_values = list(yearly_sales_dict.values())

    return yearly_sales_values




def get_weekly_sales():
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=7)
    print(start_of_week,'\n',end_of_week)
    weekly_sales = Payment.objects.filter(
        payment_time__date__range=[start_of_week, end_of_week],
        payment_status="SUCCESS"
    ).annotate(day_of_week=ExtractWeekDay('payment_time')).values('day_of_week').annotate(weekly_total=Sum('amount_paid')).order_by('day_of_week')
    print(f'week = {weekly_sales}')
    weekly_sales_values = [0] * 7
    for entry in weekly_sales:
  
        adjusted_index = entry['day_of_week'] - 2
        weekly_sales_values[adjusted_index] = entry['weekly_total']

        print(f'weekly = {weekly_sales_values}')

    return weekly_sales_values





# def get_weekly_sales():
#     today = timezone.now().date()
#     start_of_week = today - timedelta(days=today.weekday())
#     end_of_week = start_of_week + timedelta(days=6)
#     print(start_of_week, '\n', end_of_week)
    
#     weekly_sales = Payment.objects.filter(
#         payment_time__date__range=[start_of_week, end_of_week],
#         payment_status="SUCCESS"
#     ).annotate(day_of_week=ExtractWeekDay('payment_time')).values('day_of_week').annotate(weekly_total=Sum('amount_paid')).order_by('day_of_week')
    
#     print(f'week = {weekly_sales}')
    
#     weekly_sales_values = [0] * 7
#     for entry in weekly_sales:
#         adjusted_index = entry['day_of_week'] - 1  # Adjust to get a 0-based index
#         weekly_sales_values[adjusted_index] = entry['weekly_total']
#         print(f'weekly = {weekly_sales_values}')

#     return weekly_sales_values




@login_required
def custom_date_range_data(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Convert start_date and end_date strings to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Add one day to end_date

        print(f'st = {start_date}')
        print(f'ed = {end_date}')

        # Query data based on the custom date range
        custom_date_range_data = Payment.objects.filter(
            payment_time__date__range=[start_date, end_date],
            payment_status="SUCCESS"
        ).values('payment_time__date').annotate(daily_total=Sum('amount_paid')).order_by('payment_time__date')
        
        all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
        
        results_dict = {entry['payment_time__date']: entry['daily_total'] for entry in custom_date_range_data}

        data = {
            # 'labels': [entry['payment_time__date'].strftime('%Y-%m-%d') for entry in custom_date_range_data],
            # 'values': [entry['daily_total'] for entry in custom_date_range_data]
            'labels': [date.strftime('%Y-%m-%d') for date in all_dates],
            'values': [results_dict.get(date.date(), 0) for date in all_dates]
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'})


# def get_yearly_sales():
#     yearly_sales = Payment.objects.filter(
#        payment_time__year=timezone.now().year,
#         payment_status="SUCCESS"
#     ).annotate(year=ExtractYear('payment_time')).values('year').annotate(yearly_total=Sum('amount_paid')).order_by('year')

#     yearly_sales_values = [0] * 12  # Assuming you want data for each month in a year
#     for entry in yearly_sales:
#         year_index = entry['year'] - timezone.now().year 
#         print(f'year = {timezone.now().year}') # Adjust to get a 0-based index
#         yearly_sales_values[year_index] = entry['yearly_total']

#     return yearly_sales_values



def dashboard_view(request):
    dashboard_url = reverse('admin_side:dashboard')
    return render(request, 'admin/dashboard.html', {'dashboard_url': dashboard_url})



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def logout_handler(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('userauths:sign-in')
    print('hello')
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('admin_side:login')



@cache_control(no_cache=True, must_revalidate=True, max_age=0)
@login_required(login_url='userauths:sign-in')
def admin_user_handler(request):

    if request.user.is_authenticated and not request.user.is_superuser or not request.user.is_authenticated:
        return redirect('product:index')

    users = User.new_manager.all()
        
    context = {
        'users' :  users
    }
   
    return render(request, 'admin/user/user_management.html',context)



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
@login_required(login_url='userauths:sign-in')
def customer_status(request, user_id):
    if request.user.is_authenticated and not request.user.is_superuser or not request.user.is_authenticated:
        return redirect('product:index')
    
    print(user_id)
    user=get_object_or_404(User, id=user_id)
    print(user)
    if user.is_active:
            user.is_active=False
    
    else:
            user.is_active=True
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def logout_view(request):
    logout(request)
    messages.success(request, 'You logged out.')
    return redirect('userauths:sign-in')

def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_side:coupon')  # Redirect to a view that lists all coupons
    else:
        form = CouponForm()
    return render(request, 'admin/products/coupon.html', {'form': form})


def coupon(request):
    # Fetch all active coupons from the database
    coupons = Coupon.objects.all()

    # Pass the coupons to the template for rendering
    return render(request, 'admin/products/view_coupon.html', {'coupons': coupons})



def delete_coupon(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted successfully.')
        return redirect('admin_side:coupon')  # Redirect to the coupon list view
    return render(request, 'admin/products/confirm_delete_coupon.html', {'coupon': coupon})