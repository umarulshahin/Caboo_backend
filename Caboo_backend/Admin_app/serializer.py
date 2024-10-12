from rest_framework import serializers
from Driver_app.models import *
from User_app.models import *
from Authentication_app.models import *
from .models import *
from datetime import datetime


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['username', 'email', 'phone', 'is_active', 'profile','id','ride','wallet']
        read_only_fields = ['id']
        
class DriverDataSerializer(serializers.ModelSerializer):
    customuser = UserDataSerializer(read_only=True)

    class Meta:
        model = DriverData
        fields = ['aadhaar',
                  'vehicle_name',
                  'vehicle_no',
                  'rc_img',
                  'license',
                  'insurance',
                  'vehicle_photo',
                  'customuser',
                  'request',
                  'dicline_reason',
                  'comments',
                  'id',
                  'Vehicle_type']

class CouponSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Coupons
        fields=['id', 'code', 'type', 'discount', 'max_amount', 'image', 'created_at', 'start_date', 'end_date', 'status']
        read_only_fields = ['created_at','id'] 

    def validate(self, obj):
         
        today = datetime.today().date()
        start_date = obj['start_date']
        expire_date = obj['end_date']
        
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(expire_date, datetime):
            expire_date = expire_date.date()
            
        if obj['discount'] >50:
            raise serializers.ValidationError('Discount cannot be more than 50%.')
        elif start_date < today:
            raise serializers.ValidationError("Start date must be today or a future date")
        elif start_date > expire_date:
            raise serializers.ValidationError('Expire date must be greater than or equal to start date.')
        
        return obj
    def create(self, validated_data):
       
        coupons=Coupons.objects.create(
            
            code=validated_data['code'],
            type=validated_data['type'],
            discount=validated_data['discount'],
            max_amount=validated_data['max_amount'],
            image=validated_data.get('image'),
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            status=validated_data['status']
            
        )
        coupons.save()
        return coupons