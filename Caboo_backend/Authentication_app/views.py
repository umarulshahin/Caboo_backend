from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .models import *
import random
from .tasks import send_email_task
from django.conf import settings
from celery.result import AsyncResult
from .serializer import *
from rest_framework import status
import logging


from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token

CustomUser = get_user_model()
logger = logging.getLogger(__name__)

from google.auth.transport import requests


# Create your views here.

@api_view(['POST'])
def Email_validate(request):
    
     if request.method == "POST":
        data = request.data
        serializer=EmailValidationSerializer(data=data)
        if serializer.is_valid():        
            user=CustomUser.objects.filter(email=data["email"]).first()
            
            print(user)
            if user:
                if user.is_active:
                    
                    result=OTP_sender(data["email"])
                    
                    if result == "success":
                        
                        if data['role']=="Drive" :
                        
                            driver=DriverData.objects.filter(customuser=user.id).first()
                            
                            if driver and driver.request =='active':
                                
                                return Response({"success": "alredy email exist",'status':"Driver data success", "email": data['email']})
                            
                            elif driver and driver.request =='pending':
                                    
                                return Response({"success": "alredy email exist",'status':"Driver not approval", "email": data['email']})

                            else:
                                return Response({"success": "alredy email exist",'status':"Driver data is None","email": data['email'], "data":CustomUserSerializer(user).data })

                        return Response({"success": "alredy email exist", "email": data['email']})
                    else:
                        return Response({"error": "OTP generation failed, try again later"}, status=status.HTTP_400_BAD_REQUEST)
                
                else:
                    return Response({"success": "User is not active ", "email": data['email']})
                
            else:
                result=OTP_sender(data["email"])
                if result == "success":
                    return Response({"success": "New user", "email": data['email']})
                else:
                    return Response({"error": "OTP generation failed, try again later"}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response({"error":serializer.errors})
                        
def OTP_sender(email):
    
    print(email,'yes otp send is working')
    otp_code = str(random.randint(100000, 999999))
    subject = "Caboo OTP verification"
    message = f'Your OTP code is {otp_code}. It is valid for 3 minutes.'
    from_email = 'akkushahin666@gmail.com'
    recipient_list = [email]

        # Send email task (Make sure send_email_task is defined and works properly)
    result = send_email_task.delay(subject, message, from_email, recipient_list)
    response = task_status(result.id)

    if response.status_code == 200:
        
        try:
            
            otp_entry = OtpStorage.objects.get(email=email)
            otp_entry.otp = otp_code
            otp_entry.save()
            
        except OtpStorage.DoesNotExist:
            
            OtpStorage.objects.create(otp=otp_code, email=email)
        return "success"
    
    return  "email sending fail"
        
@api_view(['POST'])
def OTP_validate(request):
    
    if request.method == "POST":
        data=request.data
        serializer=OTPverifySerializer(data=data)
        
        if serializer.is_valid():
            
            return Response({"success":"OTP verified successfully","data":serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"error":serializer.errors})
        


def task_status(task_id):
    result = AsyncResult(task_id)
    
    if result.ready():
        # Task is complete
        if result.successful():
            return Response({
                'status': 'success',
                'result': result.result  # This is the result returned by the task
            })
        else:

            return Response({
                'status': 'failed',
                'result': str(result.result)  # Error message or traceback
            })
    else:

        return Response({
            'status': 'pending',
            'result': None
        })
        
    
        
@api_view(['POST'])
def Signup(request):
    
    if request.method == "POST":
        
        try:
            data=request.data
            role=request.data.get('role')
            print(role)
            serializer = SignupSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                
                if role == "Ride":
                    
                        subject="Welcome Caboo cab"
                        message=f'Congratulations ! Your account has been successfully created. Welcome to our community!'
                        from_email='akkushahin666@gmail.com'
                        recipient_list=['akkushahin666@gmail.com']
                        send_email_task.delay(subject, message,from_email,recipient_list)
                                        
                return Response({"success":"success","data":serializer.data})
            return Response({"error":serializer.errors})
            
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Token_view(request):
    serializer = CustomTokenSerializer(data=request.data)
    if serializer.is_valid():
        return Response({"success": "OTP verified successfully", 'token': serializer.validated_data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
def Driver_signup(request):
    data = request.data
    files = request.FILES
    
    custom_user_data = {
        'email': data.get('customuser[email]'),
        'username': data.get('customuser[username]'),
        'phone': data.get('customuser[phone]'),
        'profile': files.get('profile') ,
    }
    
    try:
        print(custom_user_data)
        custom_user = CustomUser.objects.get(email=custom_user_data['email'])
        
        custom_user_serializer = CustomUserSerializer(custom_user, data=custom_user_data, partial=True)
        if custom_user_serializer.is_valid():
            custom_user_serializer.save()
        else:
            return Response(custom_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except CustomUser.DoesNotExist:
        custom_user_serializer = CustomUserSerializer(data=custom_user_data)
        if custom_user_serializer.is_valid():
            custom_user = custom_user_serializer.save()
        else:
            return Response(custom_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    driver_data = {
        'customuser': custom_user.id,
        'aadhaar': data.get('aadhaar'),
        'vehicle_name': data.get('vehicle_name'),
        'vehicle_no': data.get('vehicle_no'),
        'rc_img': files.get('rc_img'),
        'license': files.get('license'),
        'insurance': files.get('insurance'),
        'vehicle_photo': files.get('vehicle_Photo'),
        'request':'pending',
        'Vehicle_type':data.get('Vehicle_type')
    }
    print(driver_data,'driver data')
    try:
        driver_instance = DriverData.objects.get(customuser=custom_user)
        driver_serializer = DriverSerializers(driver_instance, data=driver_data, partial=True)
        
    except DriverData.DoesNotExist:
        driver_serializer = DriverSerializers(data=driver_data)

    if driver_serializer.is_valid():
        driver_serializer.save()  
        
        return Response({"success": "Driver successfully created","data":driver_serializer.data}, status=status.HTTP_201_CREATED)
    return Response(driver_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def GoogleAuth(request):
    
    id_token_str = request.data.get('token')
    role = request.data.get('role')
    
    if id_token_str is None:
        return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)
        
        google_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('name', '')
        profil = idinfo.get('picture','')
        
        logger.info(f"Successfully verified credential for email: {email}")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={'username': first_name, 'profile': profil}
        )
        
        if not user.is_active:
            return Response({'error': 'User account is disabled'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if created:
            user.set_unusable_password()
            user.save() 
            created=True
            
         
        try:
            token, _ = Token.objects.get_or_create(user=user)
        except Exception as e:
            print(f'IntegrityError: {str(e)}')
            return Response({'error': 'A database error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if role =="Drive" :
                        
            driver=DriverData.objects.filter(customuser=user.id).first()
                            
            if driver and driver.request =='active':
                
                                
                return Response({"success": "alredy email exist",'status':"Driver data success",'email':user.email, "data":CustomUserSerializer(user).data })
                            
            elif driver and driver.request =='pending':
                                    
                return Response({"success": "alredy email exist",'status':"Driver not approval", "email": user.email})

            else:
                return Response({"success": "alredy email exist",'status':"Driver data is None","email": user.email, "data":CustomUserSerializer(user).data })
                
       
        response_data = {
            'token': token.key,
            'email' : user.email,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError:
        # Invalid token
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print('Unexpected error during authentication:', str(e))
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
