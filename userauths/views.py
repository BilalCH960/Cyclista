from django.shortcuts import redirect, render
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.views.decorators.cache import cache_control
import random
from userauths.models import User
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# User = settings.AUTH_USER_MODEL



def email_send(email,otp):

    send_mail(
        'Seamless OTP Verification Code',
        f'''Dear {email},

        We hope this message finds you well. At Seamless, your security and convenience are our top priorities. We're excited to help you complete your verification process, and we're just one step away.

        To verify your account, please use the following OTP (One-Time Password):

        Your OTP: {otp}

        Please note that this OTP is only valid for a single use and will expire shortly, so act swiftly.

        If you didn't initiate this verification, please contact our support team immediately.

        Thank you for choosing Seamless. We're here to make your experience as smooth as possible. If you have any questions or need assistance, don't hesitate to reach out to our support team at yourseamlesslife@gmail.com.

        Best regards,
        The Seamless Team
        ''',
        'yourseamlesslife@gmail.com',
        [email],
        fail_silently=False,
    )



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def otp_verify(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('otp_key'):
            user = authenticate(request, email=request.session.get('email'), password=request.session.get('password'))
            if user is not None:
                login(request, user)
                return redirect('product:index')
            if user is None:
                User.new_manager.create_user(
                    username = request.session['username'],
                    email = request.session['email'],
                    password = request.session['password'], 
                )
                user = authenticate(request, email=request.session.get('email'), password=request.session.get('password'))
                login(request, user)
                return redirect('product:index')            
        elif 'resend' in request.POST:
            login_otp = random.randint(100000, 999999)
            request.session['otp_key'] = str(login_otp)
            email_send(request.session.get('email'), request.session.get('otp_key'))
            messages.info(request, 'OTP resent successfully!')
        elif entered_otp != request.session.get('otp_key'):
            messages.warning(request, 'OTP is wrong !')
        elif entered_otp is None:
            messages.warning(request, 'Enter the OTP !')

    return render(request, 'otp_login.html')



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def register_view(request):

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_side:admin_dash_handler')
        return redirect('product:index')
    
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        pass2 = request.POST.get("pass2")
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        print(pass2)

        if not username:
            messages.warning(request, "Enter a username")
            return redirect('userauths:sign-up')
        try:
            validate_email(email)
        except ValidationError:
            messages.warning(request, "Invalid email or Field is empty")
            return redirect('userauths:sign-up')
        if not password:
            messages.warning(request, "Field for password 1 is not filled")
            return redirect('userauths:sign-up')
        if not pass2:
            messages.warning(request, "Field for password 2 is not filled")
            return redirect('userauths:sign-up')
        if  len(password) < 5:
            messages.warning(request, "Minimum characters required for password")
            return redirect('userauths:sign-up')
        if password != pass2:
            messages.warning(request, "Oops! The passwords don't match.")
            return redirect('userauths:sign-up')
        try:
            if User.new_manager.get(email=email):
                messages.warning(request, "Oops! The email is already in use.")
                return redirect('userauths:sign-up')
        except User.DoesNotExist:
            pass
             
        try:
           if User.new_manager.get(username=username):
                messages.warning(request, "Oops! The name is already in use.")
                return redirect('userauths:User')
        except User.DoesNotExist:
            pass
       
        login_otp = random.randint(100000, 999999)
        request.session['otp_key'] = str(login_otp)
        email_send(request.session['email'],request.session['otp_key'])
        return redirect('userauths:otp_verify') 
        
    return render(request, 'userauths/sign-up.html')

@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f'You are already logged in')
        return redirect("product:index")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email = email)
            user = authenticate(request, email=email, password=password)
       
            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in.")
                return redirect("product:index")
            else:
                messages.warning(request, "User does'nt Exist, Please create an account.")
    
        except:
            messages.warning(request, f'User with {email} does not exists')
        

    

    
    return render(request, 'userauths/sign-in.html')



@cache_control(no_cache=True, must_revalidate=True, max_age=0,no_store = True)
def logout_view(request):
    logout(request)
    messages.success(request, 'You logged out.')
    return redirect('userauths:sign-in')