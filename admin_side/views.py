from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.contrib.auth import authenticate,logout,login
from django.http import HttpResponseRedirect
from userauths.models import User
from django.urls import reverse




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




    context = {
        'user': request.user,
        
    }
    return render(request, 'admin/dashboard.html', context)



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