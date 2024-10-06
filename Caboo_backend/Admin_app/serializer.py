from rest_framework import serializers
from Driver_app.models import *
from User_app.models import *
from Authentication_app.models import *



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
