from django.urls import include, path
from userauths import  views

app_name = 'userauths'

urlpatterns = [
    path('auth/', include('social_django.urls', namespace='social')),
    path('signup/', views.register_view, name='sign-up'),
    path('signin/', views.login_view, name='sign-in'),
    path('signout/', views.logout_view, name='sign-out'),
    path('otp-verify/',views.otp_verify, name='otp_verify'),
    path('dummy/', views.dummy_view, name='dummy_view'),
]






























# from django.urls import path
# from userauths import  views

# app_name = 'userauths'

# urlpatterns = [
#     path('signup/', views.register_view, name='sign-up'),
#     path('signin/', views.login_view, name='sign-in'),
#     path('signout/', views.logout_view, name='sign-out'),
#     path('otp-verify/',views.otp_verify, name='otp_verify'),
# ]
 