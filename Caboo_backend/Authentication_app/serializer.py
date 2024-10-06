from rest_framework import serializers
from .models import *
from  Authentication_app.models import *
from rest_framework_simplejwt.tokens import RefreshToken



class EmailValidationSerializer(serializers.Serializer):
    email = serializers.EmailField()
class SignupSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = CustomUser
        fields = ['email', 'username' , 'phone', 'password','id']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    def validate(self, attrs):
        
            if CustomUser.objects.filter(email=attrs['email']).exists():
                raise serializers.ValidationError({"email": "Email already exists."})
            if CustomUser.objects.filter(phone=attrs['phone']).exists():
                raise serializers.ValidationError({"phone": "Phone number already exists."})
            return attrs
           
    def create(self, validated_data):
                
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password'],
        )
        user.save()
        return user


class OTPverifySerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        otp = attrs.get("otp")
        email = attrs.get("email")
        
        if OtpStorage.objects.filter(otp=otp, email=email).exists():
            return attrs
        else:
            raise serializers.ValidationError("OTP is invalid")
        
class CustomTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'], is_active=True)
       
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or user not active.")
        
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['role'] = user.is_staff

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'email' : user.email

        }
        
class CustomUserSerializer(serializers.ModelSerializer):
    profile = serializers.ImageField(required=False)  

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'phone', 'profile']


class DriverSerializers(serializers.ModelSerializer):
    customuser = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=True)

    class Meta:
        model = DriverData
        fields = [
            'customuser', 'aadhaar', 'vehicle_name', 'vehicle_no', 
            'rc_img', 'license', 'insurance', 'vehicle_photo','request', 'Vehicle_type'
        ]

    def validate(self, attrs):
        
        if DriverData.objects.filter(customuser=attrs.get('customuser')).exclude():
            return attrs
        
        if DriverData.objects.filter(aadhaar=attrs.get('aadhaar')).exists():
            raise serializers.ValidationError({"aadhaar": "Aadhaar already exists"})
        if DriverData.objects.filter(vehicle_no=attrs.get('vehicle_no')).exists():
            raise serializers.ValidationError({"vehicle_no": "Vehicle Number already exists"})
        return attrs

    def create(self, validated_data):
        driver_data = DriverData.objects.create(
            customuser=validated_data.get('customuser'),
            aadhaar=validated_data.get('aadhaar'),
            vehicle_name=validated_data.get('vehicle_name'),
            vehicle_no=validated_data.get('vehicle_no'),
            rc_img=validated_data.get('rc_img'),
            license=validated_data.get('license'),
            insurance=validated_data.get('insurance'),
            vehicle_photo=validated_data.get('vehicle_photo'),
            request=validated_data.get('request'),
            Vehicle_type=validated_data.get('Vehicle_type')
        )
        return driver_data
