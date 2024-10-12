from django.db import models
from Authentication_app.models import *
import random
import string
from django.utils import timezone
from Admin_app.models import *


class DriverLocation(models.Model):
    user_id = models.IntegerField()
    driver_id = models.IntegerField()
    location = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('driver_id', 'timestamp')

class TripDetails(models.Model):
    
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='Trip_user')
    driver = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='Trip_driver')
    location = models.CharField(max_length=250,blank=False)
    destination = models.CharField(max_length=250,blank=False)
    distance = models.CharField(max_length=50,blank=False)
    duration = models.CharField(max_length=50,blank=False)
    amount = models.IntegerField(blank=True,null=True)
    orderId = models.CharField(max_length=12, unique=True, blank=True)
    tripOTP = models.CharField(max_length=10,blank=False)
    status = models.CharField(max_length=20,blank=False)
    payment_type = models.CharField(max_length=50,blank=True)
    dateTime = models.DateTimeField(default=timezone.now)
    service_type = models.CharField(max_length=200,null=False,blank=False)
    rating = models.IntegerField(null=True,blank=True)
    message = models.TextField(null=True,blank=True)
    
     
    def save(self, *args, **kwargs):
        if not self.orderId:
            self.orderId = self.generate_order_id()
        super().save(*args, **kwargs)

    def generate_order_id(self):

        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))        


class UserWallet(models.Model):
    
    customuser=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    amount = models.IntegerField(blank=False,null=False,default=0)
    created_at = models.DateTimeField(default=timezone.now)
    reason = models.CharField(max_length=250,null=True,blank=True)
    status = models.CharField(max_length=50,blank=False,null=False)
    
    
class UsedCoupons(models.Model):
    
    User_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    Coupon_id = models.ForeignKey(Coupons,on_delete=models.CASCADE)
    used_at = models.DateTimeField(default=timezone.now)