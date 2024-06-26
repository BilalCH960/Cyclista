import traceback
from django.http import JsonResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_control
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views
from account.forms import ImageForm
from django.contrib import messages
from order.models import *
from psycopg2 import IntegrityError
from account.models import Address
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from product.models import User
from .models import UserProfile
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
import shortuuid
from django.utils.translation import gettext as _
import random
import string
import re
import pycountry
from wallet.models import Referral, EasyPay
from django.core.exceptions import ObjectDoesNotExist



@cache_control(no_cache=True, must_revalidate=True, max_age=0, no_store=True)
def my_dashboard(request):
        if not request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin_side:login')
            messages.warning(request,'Account Blocked, Please use another account')
            return redirect('userauths:sign-in')

        shipping = Address.objects.filter(user=request.user, is_shipping=True, is_default=True)
        orders = Order.objects.filter(user=request.user).order_by('-order_update_time')
        billing = Address.objects.filter(user=request.user, is_billing=True, is_default=True)
        UserProfile.objects.get_or_create(user=request.user)  
        

        try:
            referral = Referral.objects.get(user=request.user)
        except Referral.DoesNotExist:
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))  # Generate a random code
            referral = Referral.objects.create(user=request.user, referral_self=referral_code)
        
        easywallet, _ = EasyPay.objects.get_or_create(user = request.user)

        print(f'easy = {easywallet}')
        context = {
            'shipping': shipping,
            'orders': orders,
            'billing': billing,
            'ref': referral.referral_self,
            'easy': easywallet,
            # 'total':total,
            'myuser': UserProfile.objects.get(user=request.user),
        }
        return render(request, 'user/dashboard/dashboard.html', context)
    


def order_detail(request, id):
    order = Order.objects.get(user = request.user, id=id)
    order_items = OrderItem.objects.filter(order=order)


    context = {
        'order_items' : order_items
    }
    return render(request, 'user/dashboard/order-detail.html', context)


@login_required
@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def add_address(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    
    if request.method=="POST":
        try:
            user = request.user
            name =request.POST.get('name')
            if name.strip() == '':
                messages.warning(request, 'Name is required')
                return redirect('account:add_address')
                
            phone_number = request.POST.get('phone_number')
            if phone_number.strip() == '' or not phone_number.isdigit():
                messages.warning(request, 'Number must be an integer')
                return redirect('account:add_address')
            address_one = request.POST.get('house_address')
            if address_one.strip() == '':
                messages.warning(request, 'Address is required')
                return redirect('account:add_address')
            city =request.POST.get('city')
            if city.strip() == '':
                messages.warning(request, 'City is required')
                return redirect('account:add_address')
            state =request.POST.get('state')
            if state.strip() == '':
                messages.warning(request, 'State is required')
                return redirect('account:add_address')
            country = request.POST.get('country')
            if country.strip() == '':
                messages.warning(request, 'Country is required')
                return redirect('account:add_address')
            pincode =request.POST.get('pincode')
            if pincode.strip() == '' or not pincode.isdigit():
                messages.warning(request, 'Pincode must be an integer')
                return redirect('account:add_address')
            print("Attempting to create Address with the following data:")
            print(f"User: {user}")
            print(f"Name: {request.POST.get('name')}")
            print(f"country: {request.POST.get('country')}")
            print(f"house_address: {request.POST.get('house_address')}")

            Address.objects.create(
                user = user,
                name =name,
                phone_number = phone_number,
                address_one = address_one,
                city = city,
                state = state,
                country = country,
                pincode = pincode,
                is_shipping = True if 'as_shipping' in request.POST else False,
                is_billing = True if 'as_billing' in request.POST else False,
            )
            messages.success(request,'the address has been added')
            return redirect('account:add_address')
        except IntegrityError as e:
            messages.warning(request, f'The address could not be added. Error: {str(e)}')
            traceback.print_exc()


    return render(request, 'user/dashboard/address.html')


@login_required
def manage_address(request):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    
    try:
        context = {
        'shipping_address':Address.objects.filter(Q(is_shipping = True) & Q(user= request.user) & ~Q(is_default = True)),
        'billing_address':Address.objects.filter(Q(is_billing = True) & Q(user= request.user) & ~Q(is_default = True)),
        'default_billing':Address.objects.filter(Q(is_billing = True) & Q(user= request.user) & Q(is_default = True)),
        'default_shipping':Address.objects.filter(Q(is_shipping = True) & Q(user= request.user) & Q(is_default = True)),
        'all_address':  Address.objects.filter(user = request.user, is_billing=False, is_shipping=False),
        }
    except Exception as e:
        print(f'the error is {e}')
    
    return render(request, 'user/dashboard/manage_address.html',context)



@login_required
@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def edit_address(request,id):
    if not request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('admin_side:login')
        return redirect('product:index')
    address = get_object_or_404(Address, (Q(user = request.user) & Q(id=id)))
    if request.method == "POST":
        user = request.user
    try:
        address.name =request.POST['name']
        if address.name.strip() == '':
                messages.warning(request, 'Name is required')
                return redirect('account:edit_address')
        elif not address.name.strip().isalpha() :
            messages.warning(request, 'Name must be alphabets')
            return redirect('account:edit_address')
        address.phone_number = request.POST['phone_number']
        if address.phone_number.strip() == '' or not address.phone_number.isdigit():
                messages.warning(request, 'Number must be an integer')
                return redirect('account:edit_address')
        elif len(address.phone_number) < 10:
            messages.warning(request, 'Number must be 10 digits')
            return redirect('account:edit_address')
        address.address_one = request.POST['house_address']
        if address.address_one.strip() == '':
                messages.warning(request, 'Address is required')
                return redirect('account:edit_address')
        address.city =request.POST['city']
        if address.city.strip() == '':
                messages.warning(request, 'City is required')
                return redirect('account:edit_address')
        elif not address.city.strip().isalpha():
            messages.warning(request, 'City must be alphabets')
            return redirect('account:edit_address')
        address.state =request.POST['state']
        if address.state.strip() == '':
                messages.warning(request, 'State is required')
                return redirect('account:edit_address')
        elif not address.state.strip().isalpha():
            messages.warning(request, 'State must be alphabets')
            return redirect('account:edit_address')
        address.country = request.POST['country']
        if address.country.strip() == '':
                messages.warning(request, 'Country is required')
                return redirect('account:edit_address')
        elif not address.country.strip().isalpha():
            messages.warning(request, 'Country must be alphabets')
            return redirect('account:edit_address')
        elif not pycountry.countries.get(name=address.country):
            messages.warning(request, 'Please enter a valid country')
            return redirect('account:edit_address')
        address.pincode =request.POST['pincode']
        if address.pincode.strip() == '' or not address.pincode.isdigit():
                messages.warning(request, 'Pincode must be an integer')
                return redirect('account:edit_address')
        elif len(address.pincode) < 6:
            messages.warning(request, 'Pincode must be 6 digits')
            return redirect('account:edit_address')
        address.is_billing = True if 'as_billing' in request.POST else False
        address.is_shipping = True if 'as_shipping' in request.POST else False
        address.is_default = True if 'set_default' in request.POST else False
        address.save()
        messages.success(request,f'the address {address.address_one} has saved changes')
        return redirect('account:manage_address')
    except:
        pass
    context = {
        'add':address,
    }
    return render(request, 'user/dashboard/address_edit.html', context)

@login_required
def del_address(request,id):
    address = get_object_or_404(Address, user = request.user, id=id)
    messages.info(request,f'the address {address} has been deleted')
    address.delete()
    return redirect('account:manage_address')


@login_required
def account_edit(request):
    if request.method =="POST":
        acc_user, check = UserProfile.objects.get_or_create(user = request.user)
        acc_user.full_name = request.POST.get('name')
        if acc_user.full_name.strip() == "":
             messages.warning(request,'Please enter your name.')
             return redirect('account:account_edit')
        elif not re.match(r'^[a-zA-Z\s]+$', acc_user.full_name.strip()):
            messages.warning(request, 'Please enter a valid name.')
            return redirect('account:account_edit')
        
        acc_user.phone_number = request.POST.get('phnumber') if request.POST.get('phnumber') else request.user.phone_number
        acc_user.email = request.POST.get('email') if request.POST.get('email') else request.user.email
        if request.FILES.get('Profile_img'):
            acc_user.profile_pic = request.FILES.get('Profile_img')
        if request.POST.get('nationality'):
            acc_user.nationality = request.POST.get('nationality')
            if acc_user.nationality.strip() == "":
                messages.warning(request,'Please enter your nationality.')
                return redirect('account:account_edit')
        print(request.POST.get('nationality'))
        # if not acc_user.DOB:
        #     acc_user.DOB = request.POST['DOB']
        try:
            acc_user.save()
            messages.success(request,'Account details updated successfully!')
            return redirect('account:account_edit')
        except Exception as e:
            print(F'the error {e}')
            messages.error(request,f"An error occured while updating your profile.{e}")
            pass
    myuser = UserProfile.objects.get_or_create(user = request.user)
    myuser = get_object_or_404(UserProfile, user = request.user)
    print(myuser)
    context = {
        'myuser' : myuser
    }

    return render(request, 'user/dashboard/edit_account.html', context)




# class PasswordChangeView(PasswordChangeView):
#     form_class = PasswordChangeForm
#     success_url = reverse_lazy('account:account_edit')




class CustomPasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """

    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _("Your old password was entered incorrectly. Please enter it again."),
        "password_complexity": _("Your password must contain at least one special character, one uppercase letter, and one number."),
    }

    old_password = forms.CharField(
        label=_("Old Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )

    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean(self):
        """
        Validate old password and new password complexity.
        """
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')

        # Check if old password is correct
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )

        # Check new password complexity
        if new_password1:
            if not re.search(r'(?=.*[!@#$%^&*()_+}{":;\'?><,./\[\]\|`~])', new_password1) \
                    or not re.search(r'(?=.*[A-Z])', new_password1) \
                    or not re.search(r'(?=.*\d)', new_password1):
                raise ValidationError(
                    self.error_messages["password_complexity"],
                    code="password_complexity",
                )

        return cleaned_data



class CustomPasswordChangeView(auth_views.PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('account:account_edit')
    success_message = _("Your password was changed successfully.")  # Success message

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)  # Add success message
        return response
