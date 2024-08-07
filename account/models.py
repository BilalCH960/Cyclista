# Create your models here.
from product.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=60,blank=True, default='', null=True)
    email = models.EmailField(max_length=60,blank=True, default='', null=True)
    phone_number = models.CharField(max_length=15, default='', blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pic/", blank=True, null=True, default='')
    nationality = models.CharField(max_length=50, null=True, blank=True)


    def save(self,*args, **kwargs):
        # automatically adding user name and phone number is None is found
        if not self.full_name:
            self.full_name = self.user.username
        if not self.phone_number:
            self.phone_number = self.user.phone_number
        super(UserProfile, self).save(*args, **kwargs)


    def __str__(self):
        return self.full_name


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=40)
    phone_number = models.CharField(max_length=15)
    address_one = models.CharField(max_length=60)
    address_two = models.CharField(max_length=60, null=True, blank=True)
    city =models.CharField(max_length=50)
    state =models.CharField(max_length=50)
    country =models.CharField(max_length=50)
    pincode =models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)
    is_shipping = models.BooleanField(default=False)
    is_billing = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.is_default:
            if self.is_shipping:
                Address.objects.filter(user=self.user, is_shipping=True).exclude(pk=self.pk).update(is_default=False)
            elif self.is_billing:
                Address.objects.filter(user=self.user, is_billing=True).exclude(pk=self.pk).update(is_default=False)
        super(Address, self).save(*args, **kwargs)


    def FullAddress(self):  
        address = [self.name,self.address_one]
        if self.address_two:
            address.append(self.address_two)
        address.extend([self.city, self.state, self.country])
        return ', '.join(address)
        
    def __str__(self):
        return f'{self.name} {self.address_one}' 
        