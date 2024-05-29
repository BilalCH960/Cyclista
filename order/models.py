import uuid
from django.db import models
from product.models import User
from cart.models import Coupon
from decimal import Decimal
from account.models import Address
from ad_product.models import ProductVariant
from django.utils.html import mark_safe

 


class Payment(models.Model):
    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
        ("REFUNDED", "Refunded"),
    )
    PAYMENT_METHOD = (
        ('COD', 'Cash On Delivery'),
        ('RazorPay', 'Razor Pay'),
        ('Wallet', 'Wallet')

    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=20)
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True)
    payment_signature = models.CharField(max_length=100,null=True,blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_time = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.payment_method == 'COD' or self.payment_method == 'Wallet':
            self.razorpay_payment_id = None
        elif self.payment_method == 'RazorPay':
            self.payment_id = None
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.payment_id) if self.payment_id else str(self.razorpay_payment_id)
    
    
class Order(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_details = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.AutoField(primary_key=True)
    shipping_address = models.CharField(max_length=500, null = True)
    billing_address = models.CharField(max_length=500, null = True)
    order_total = models.DecimalField(max_digits=12, decimal_places=2)
    order_subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    order_shipping = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    order_coupon = models.ForeignKey(Coupon,   blank=True, null = True,  on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    order_time = models.DateTimeField(auto_now_add=True)
    order_update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.user} - {self.order_number}"

    def get_sales_amount(self):
        return self.order_total - (self.order_shipping or 0)
    
    def get_actual_discount(self):
        if self.order_coupon and self.order_subtotal:
            discount_amount = (self.order_subtotal * self.order_coupon.discount) / 100
            return min(discount_amount, self.order_coupon.max_discount_amount)
        return 0
    


    
class OrderItem(models.Model):
    ORDER_STATUS = (
        ("PLACED", "Order Placed"),
        ("PROCESSING", "Order Processing"),
        ("SHIPPED", "Order Shipped"),
        ("OUT FOR DELIVERY", "Out For Delivery"),
        ("DELIVERED", "Order Delivered"),
        ("CANCELLED", "Order Cancelled"),
        ("RETURNED", "Order Returned"),
    )  
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    order_item_id = models.CharField(max_length=120, default='#0000000')
    order_status = models.CharField(choices=ORDER_STATUS, max_length=20, default='PROCESSING')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null = True) 
    order_product = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null = True)
    quantity = models.IntegerField(default= 1)
    payment_details = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    product_price = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
    ordered_time = models.DateTimeField(auto_now_add=True)
    order_updated_time = models.DateTimeField(auto_now=True)
    cancel_reason = models.TextField(max_length=200, null=True, blank=True)
    soft_delete = models.BooleanField

    def __str__(self):
        return f"Order {self.user}"
    def get_total(self):
        return self.quantity * self.product_price
    




