from django.db import models
from django.utils import timezone
import os

# Create your models here.
def truncate_filename(instance, filename, subfolder):
    filename_base, filename_ext = os.path.splitext(filename)
    truncated_filename = filename_base[:100] + filename_ext
    return os.path.join('img/coupon', subfolder, truncated_filename)

def upload_coupon_image(instance, filename):
    return truncate_filename(instance, filename, 'coupon')

class Coupons(models.Model):
    
    code = models.CharField(max_length=100,null=False,blank=False)
    type = models.CharField(max_length=100,null=False,blank=False)
    discount = models.IntegerField(null=False,blank=False)
    max_amount = models.IntegerField(null=False,blank=False)
    image = models.ImageField(upload_to=upload_coupon_image, blank=False, max_length=250)
    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(blank=False,null=False)
    end_date = models.DateTimeField(blank=False,null=False)
    status = models.BooleanField(default=False,null=False)

    