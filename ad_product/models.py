from django.db import models
from django.utils.text import slugify
from category_manage.models import Category
from django.utils.html import mark_safe
from decimal import Decimal
from django.db.models import UniqueConstraint, Q
from colorfield.fields import ColorField


# app_name = ad_product


STATUS = (
    ("draft","Draft"),
    ("disabled","Disabled"),    
    ("rejected","Rejected"),
    ("in_review","In Review"),
    ("published","Published"),
)



class Brand(models.Model):
    brand_name = models.CharField(max_length=30)
    brand_img = models.ImageField(upload_to='brand_logo/', default="")
    is_active = models.BooleanField(default=True)
    soft_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.brand_name



class Product(models.Model):
    product_name = models.CharField(max_length=49,unique=False, null=False)
    product_catg = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name = "category")
    product_slug = models.SlugField(unique=False, blank=True, max_length=200)
    product_img = models.ImageField(upload_to='mproducts/',null=True,blank=True)
    product_description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    product_brand = models.ForeignKey(Brand,on_delete=models.CASCADE, null = True)
    soft_delete = models.BooleanField(default=False)


    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def save(self, *args, **kwargs):
        product_slug_name = '-'.join([
            self.product_name,
            self.product_catg.category_name,
        ])
        base_slug = slugify(product_slug_name)
        self.product_slug = base_slug
        super(Product, self).save(*args, **kwargs)

    def __str__(self):

        return f"{self.product_name}"
    
    def soft_delete_instance(self):
        self.soft_delete = True
        self.save()

    def restore_instance(self):
        self.soft_delete = False
        self.save()

    def is_soft_deleted(self):
        return self.soft_delete

    
    
class ProductImages(models.Model):
    images = models.ImageField(upload_to='product-images', default='product.jpg')
    product = models.ForeignKey(Product,related_name='p_images', on_delete=models.SET_NULL, null = True)
    date = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name_plural = 'Product Images'



class ProductOffer(models.Model):
    product_name = models.OneToOneField(Product, on_delete = models.CASCADE)
    discount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.0)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default= False)

    def __str__(self):
        return f'{self.product_name} - RS {self.discount}'



class Attribute(models.Model):
    attribute_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.attribute_name
    


class AttributeValue(models.Model):
    Attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    Attribute_value = models.CharField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self)->str:
        return f"{self.Attribute} : {self.Attribute_value}"
    


class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE ,related_name='product_variants')
    model_id = models.CharField(max_length=30, unique=True,null=False)
    color = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock = models.IntegerField()
    product_varient_slug = models.SlugField(unique=True, blank=True,max_length=350)
    product_status = models.CharField(choices = STATUS, max_length=10, default = 'in_review')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=500, blank=True)
    featured = models.BooleanField(default = False)
    soft_delete = models.BooleanField(default=False)

    def get_percentage(self):
        new_price = 100 - (self.sale_price / self.max_price) * 100
        return new_price


    def save(self, *args,**kwargs):
        base_slug = '-'.join([
            self.product.product_name,
            self.product.product_catg.category_name,
            self.model_id,
        ])
        self.product_varient_slug = slugify(base_slug)
        super(ProductVariant, self).save(*args, **kwargs)

    def soft_delete_instance(self):
        self.soft_delete = True
        self.save()

    def restore_instance(self):
        self.soft_delete = False
        self.save()

    def is_soft_deleted(self):
        return self.soft_delete




    class Meta:
        constraints = [
            UniqueConstraint(
                name="unique_skuid_must_be_provided",
                fields=['product', 'model_id'],
                condition=Q(model_id__isnull=False)
            )
        ]


    
    def name(self):
        return f'{self.product.product_name} {self.color}'

    
    def get_variant_name(self):

        return f"{self.product.product_name} (Color : {self.color.Attribute_value}, PRICE: {self.sale_price})"
    
    
class VariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='varient_img/')

    def __str__(self):
        return f"Images for {self.variant.product_varient_slug}"

