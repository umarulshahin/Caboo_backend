from django.db import models
from django.utils import timezone
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Utility function to truncate filenames
def truncate_filename(instance, filename, subfolder):
    filename_base, filename_ext = os.path.splitext(filename)
    truncated_filename = filename_base[:100] + filename_ext
    return os.path.join('img', subfolder, truncated_filename)

def upload_profile_image(instance, filename):
    return truncate_filename(instance, filename, 'profile')

def upload_vehicle_image(instance, filename):
    return truncate_filename(instance, filename, 'vehicle')

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=30, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=10, blank=True,null=True, unique=True)
    profile = models.ImageField(upload_to=upload_profile_image, blank=False, max_length=250)
    ride = models.BooleanField(default=False,blank=False)
    wallet = models.IntegerField(default=0,blank=True,null=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class OtpStorage(models.Model):
    otp = models.CharField(max_length=10, blank=False)
    email = models.EmailField(unique=True, blank=False)

class DriverData(models.Model):
    
    TYPE_CHOICE = [
        ('Bike', 'Bike'),
        ('Car', 'Car'),
        ('Auto', 'Auto')
    ]
    
    customuser = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    aadhaar = models.CharField(max_length=15, blank=False, unique=True)
    vehicle_name = models.CharField(max_length=100, blank=False)
    vehicle_no = models.CharField(max_length=15, blank=False)
    rc_img = models.ImageField(upload_to=upload_vehicle_image, blank=False, max_length=250)
    license = models.ImageField(upload_to=upload_vehicle_image, blank=False, max_length=250)
    insurance = models.ImageField(upload_to=upload_vehicle_image, blank=False, max_length=250)
    vehicle_photo = models.ImageField(upload_to=upload_vehicle_image, blank=False, max_length=250)
    request = models.CharField(max_length=20,default="pending")
    dicline_reason = models.CharField(max_length=150,default="No reason provided")
    comments = models.TextField(default='No comments provided')
    current_Status = models.BooleanField(blank=False,default=False)
    Vehicle_type = models.CharField(max_length=20,choices=TYPE_CHOICE,blank=False,null=False)
