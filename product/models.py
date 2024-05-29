from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from decimal import Decimal
from PIL import Image
from ad_product.models import *


STATUS_CHOICE = (
    ("process","Processing"),
    ("shipped","Shipped"),
    ("delivered","Delivered"),
)

STATUS = (
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In Review"),
    ("published","Published"),
)

RATING = (
    (1,"⭐"),
    (2,"⭐⭐"),
    (3,"⭐⭐⭐"),
    (4,"⭐⭐⭐⭐"),
    (5,"⭐⭐⭐⭐⭐"),
)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

  


    

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet='sdfe12389')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path, default = 'product.jpg')
    description = models.TextField(null=True, blank= True, default='This is the product')

    price = models.DecimalField(max_digits= 9, decimal_places=2, default = Decimal('1.99'))
    old_price = models.DecimalField(max_digits= 9, decimal_places=2, default = Decimal('2.99'))

    specification = models.TextField(null=True, blank= True)
    stock_count = models.CharField(max_length=100, default="10")
    warranty = models.CharField(max_length=100, default='6 months', null=True, blank= True)
    mfd = models.DateTimeField(auto_now_add = False, null=True, blank= True)

    # tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True)

    product_status = models.CharField(choices = STATUS, max_length=10, default = 'in_review')

    status = models.BooleanField(default = True)
    in_stock = models.BooleanField(default = True)
    featured = models.BooleanField(default = False)
    digital = models.BooleanField(default = False)

    sku = ShortUUIDField(unique=True, length=5, max_length=99999, prefix = 'sku', alphabet='123456789')
    date = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(null = True, blank = True)

    class Meta:
        verbose_name_plural = 'Products'

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
    def get_percentage(self):
        new_price = 100 - (self.price / self.old_price) * 100
        return new_price
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            if img.height > 1000 or img.width > 1000:  # Adjust size as needed
                output_size = (1000, 1000)  # Adjust dimensions as needed
                img.thumbnail(output_size)
                img.save(self.image.path)

    

class ProductImages(models.Model):
    images = models.ImageField(upload_to='product-images', default='product.jpg')
    product = models.ForeignKey(Product,related_name='p_images', on_delete=models.SET_NULL, null = True)
    date = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name_plural = 'Product Images'



class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, related_name = "reviews")
    review = models.TextField(default = None)
    rating = models.IntegerField(choices = RATING, default = None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product Reviews'
    

    def __str__(self):
        return str(self.product.product)
    
    def get_rating(self):
        return self.rating
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    wish_item = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'wishlists'
    

    def __str__(self) -> str:
        return f"{self.my_user} - {self.wish_item}"

