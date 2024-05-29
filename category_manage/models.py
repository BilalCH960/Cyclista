from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe

# app_name = category_manage


class Category(models.Model):
    category_name = models.CharField(max_length=30, unique=True)
    description = models.TextField(max_length=200, blank=True)
    category_img = models.ImageField(upload_to='imgs/category_imgs', null=True, blank=True)
    slug = models.SlugField(max_length=30, unique=False)
    is_available = models.BooleanField(default=True)
    soft_delete = models.BooleanField(default=False)

    class Meta:
        app_label = 'category_manage'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self,*args,**kwargs):
        self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.category_name

class CategoryOffer(models.Model):
    category_name = models.OneToOneField(Category, on_delete = models.CASCADE)
    discount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=0.0)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default= False)

    def __str__(self):
        return f'{self.category_name} - RS {self.discount}'

        