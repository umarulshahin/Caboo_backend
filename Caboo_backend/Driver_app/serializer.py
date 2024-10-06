from rest_framework import serializers
from User_app.models import *
from Authentication_app.models import *
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'profile', 'id', 'is_active', 'wallet']
        read_only_fields = ['id']
class DriverDataSerializer(serializers.ModelSerializer):
    customuser = UserSerializer(read_only=True)

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
                  'current_Status',
                  'id',
                  'Vehicle_type']

