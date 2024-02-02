from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomNewManager(BaseUserManager):

    def create_superuser(self, email, username, password,phone_number, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not email:
            raise ValueError(_('The Email field must be set'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError('you are not a staff to be superuser')
        user = self.create_user(email,username,password,phone_number,**extra_fields)
        return user
    
    def create_user(self, username, email, password=None, phone_number=None, **extra_fields):
        if not email:
            raise ValueError('need email to create a user')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, phone_number= phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractUser):
  email = models.EmailField(unique = True, null = False)
  username = models.CharField(max_length=100)
  phone_number = models.CharField(max_length=15, null=True, blank=True)
  start_time = models.DateTimeField(default=timezone.now)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  is_superuser = models.BooleanField(default=False)
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username', 'phone_number']

  def __str__(self):
    return self.username
  

