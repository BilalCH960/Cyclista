import uuid
from django.db import models
from order.models import OrderItem
from order.models import Payment
from shortuuidfield import ShortUUIDField
from product.models import User

# Create your models here.
class EasyPay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.0)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username 


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    order_id = models.CharField(max_length=250, blank=True, null=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True, blank=True)
    is_debit = models.BooleanField(default=False)
    easypay = models.ForeignKey(EasyPay, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username 


class Referral(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    referral = models.CharField( null=True, blank=True, unique= False)
    referral_self = models.CharField(max_length=8, unique=True, null=True, blank=True)
  
    def __str__(self):
        return self.referral_self