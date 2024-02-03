from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User
from decimal import Decimal
from PIL import Image


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
    (1,"★☆☆☆☆"),
    (2,"★★☆☆☆"),
    (3,"★★★☆☆"),
    (4,"★★★★☆"),
    (5,"★★★★★"),
)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix='cat', alphabet='sdfjhgcase88955124')
    title = models.CharField(max_length=100, default = 'Cycles')
    image = models.ImageField(upload_to='category', default='category.jpg')

    class Meta:
        verbose_name_plural = 'Categories'

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    

class Tags(models.Model):
    pass
  

class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, max_length=20, prefix='ven', alphabet='sdfjhgcase88955124')
    title = models.CharField(max_length=100, default= 'Cyclista')
    image = models.ImageField(upload_to=user_directory_path, default = 'product.jpg')
    description = models.TextField(null=True, blank= True, default='I am a vendor')
    address = models.CharField(max_length=100, default='no address provided')
    contact = models.CharField(max_length=100, default='(123) 456 789')
    shipping_on_time = models.CharField(max_length=100, default='100')
    trust_rating = models.CharField(max_length=100, default='100')
    days_return = models.CharField(max_length=100, default='14')
    warranty_period = models.CharField(max_length=100, default='6 months')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = 'Vendors'

    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet='sdfe12389')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    

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




####################### Cart, Order ,OrderItems #######################
####################### Cart, Order ,OrderItems #######################
####################### Cart, Order ,OrderItems #######################



class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    price = models.DecimalField(max_digits= 9, decimal_places=2, default = Decimal('1.99'))
    paid_status = models.BooleanField(default = False)
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices = STATUS_CHOICE , max_length=30, default = 'processing')

    class Meta:
        verbose_name_plural = 'Cart Order'

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete= models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default = 0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal('1.99'))
    total = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal('1.99'))

    class Meta:
        verbose_name_plural = 'Cart Order Items'

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image))
 


####################### Product Review , wishlist ,address #######################
####################### Product Review , wishlist ,address #######################
####################### Product Review , wishlist ,address #######################
    



class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    review = models.TextField()
    rating = models.IntegerField(choices = RATING, default = None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product Reviews'
    

    def __str__(self):
        return self.product.title
    
    def get_rating(self):
        return self.rating
    

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'wishlists'
    

    def __str__(self):
        return self.product.title


class Address(models.Model):
    user = models.ForeignKey(User, on_delete= models.SET_NULL, null=True)
    address = models.CharField(max_length=100, null = True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'
