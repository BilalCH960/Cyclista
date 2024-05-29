from django.db import models
from product.models import User
from ad_product.models import ProductVariant


class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discount = models.DecimalField(decimal_places=2, max_digits=8)
    max_discount_amount = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True, default=10000)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code}"
    
    @property
    def discount_percentage(self):
        return (self.discount * 100) / 100
    
    def coupon_name(self):
        return f"{self.code}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null = True)
    total = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
    sub_total = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
    shipping = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}-cart'

    

class Cart_Item(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default= 1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.cart}-item - {self.product}"
    
    














































# from django.db import models
# from product.models import User
# from ad_product.models import ProductVariant
    

    
# class Cart(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     total = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
#     sub_total = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
#     shipping = models.DecimalField(decimal_places=2, max_digits=10,default=0, null=True)
#     created_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.user}-cart'

    

# class Cart_Item(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     product = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
#     quantity = models.IntegerField(default= 1)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.cart}-item - {self.product}"
    
    