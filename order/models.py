import uuid
from django.db import models
from product.models import User
from decimal import Decimal
from account.models import Address
from ad_product.models import ProductVariant
from django.utils.html import mark_safe

 


class Payment(models.Model):
    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
    )
    PAYMENT_METHOD = (
        ('COD', 'Cash On Delivery'),

    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=20)
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.payment_id)
    
    
class Order(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_details = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.AutoField(primary_key=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_address')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='billing_address')
    order_total = models.DecimalField(max_digits=12, decimal_places=2)
    order_subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    order_shipping = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    order_time = models.DateTimeField(auto_now_add=True)
    order_update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.user} - {self.order_number}"
    

    
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
    order_status = models.CharField(choices=ORDER_STATUS, max_length=20, default='PLACED')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null = True) 
    order_product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default= 1)
    payment_details = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    product_price = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
    ordered_time = models.DateTimeField(auto_now_add=True)
    order_updated_time = models.DateTimeField(auto_now=True)
    cancel_reason = models.TextField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Order {self.user}"
    def get_total(self):
        return self.quantity * self.product_price
    




    

    
















# STATUS_CHOICE = (
#     ("processing","Processing"),
#     ("shipped","Shipped"),
#     ("delivered","Delivered"),
# )


# class CartOrder(models.Model):
#     user = models.ForeignKey(User, on_delete= models.CASCADE)
#     price = models.DecimalField(max_digits= 9, decimal_places=2, default = Decimal('1.99'))
#     paid_status = models.BooleanField(default = False)
#     order_date = models.DateTimeField(auto_now_add=True)
#     product_status = models.CharField(choices = STATUS_CHOICE , max_length=30, default = 'processing')

#     class Meta:
#         verbose_name_plural = 'Cart Order'

# class CartOrderItems(models.Model):
#     order = models.ForeignKey(CartOrder, on_delete= models.CASCADE)
#     product_status = models.CharField(max_length=200)
#     item = models.CharField(max_length=200)
#     image = models.CharField(max_length=200)
#     qty = models.IntegerField(default = 0)
#     price = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal('1.99'))
#     total = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal('1.99'))

#     class Meta:
#         verbose_name_plural = 'Cart Order Items'

#     def cartItemImage(self):
#         return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

#     def order_img(self):
#         return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))




