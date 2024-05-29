from django import forms
from cart.models import Coupon
from django.forms import DateInput


class CouponForm(forms.ModelForm):
    
    valid_to = forms.DateField(widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Coupon
        fields = ['code', 'discount','max_discount_amount' , 'valid_to', 'is_active']
