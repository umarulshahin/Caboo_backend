from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from User_app.models import *
from django.conf import settings
from celery.result import AsyncResult
from rest_framework.permissions import IsAuthenticated
from .serializer import *
from Driver_app.models import *
from Authentication_app.models import *
from Authentication_app.tasks import *
from Authentication_app.views import *
from User_app.serializer import *


from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
class RoleBasedPermission(BasePermission):


    def has_permission(self, request, view):
        
        try:
            auth = JWTAuthentication()
            user, token = auth.authenticate(request)

            role = token.payload.get('role')
         
            if role :
                return True
            else:
                raise PermissionDenied("You do not have permission to access this resource.")

        except AuthenticationFailed:
            raise PermissionDenied("Invalid token or token missing.")
        except Exception as e:
            raise PermissionDenied(f"Error occurred: {str(e)}")
        


@api_view(["GET"])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Get_admin(request):
    
    admin_id = request.GET.get('id', None)
    user=CustomUser.objects.get(id=admin_id)
    if user:
        serializer=UserDataSerializer(user)
        return Response(serializer.data)

    return Response({"error":"somting wrong"},status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Get_users(request):

    users=CustomUser.objects.filter(is_staff=False)
    
    if users:
            
        serializer=UserDataSerializer(users,many=True)
        return Response(serializer.data)

    return Response({"error":"somting wrong"},status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Get_Drivers(request):
    
    try:
        users = DriverData.objects.all().prefetch_related("customuser")
        if users:
            
            serializer=DriverDataSerializer(users,many=True)
            return Response(serializer.data)

        return Response({"error":"somting wrong"},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        
        return Response(f"error {e}")
   


@api_view(["POST"])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Status_management(request):
    
        data = request.data
        try:
            user = CustomUser.objects.get(id=data["id"])
        except CustomUser.DoesNotExist:
            return Response({"error": "User not valid"}, status=status.HTTP_404_NOT_FOUND)
        
        if data["action"] == "block":
            user.is_active = False
        else:
            user.is_active = True

        user.save()  

        serializer = UserDataSerializer(user)
        return Response({"success": f"User {'blocked' if data['action'] == 'block' else 'unblocked'} successfully", "user": serializer.data}, status=status.HTTP_200_OK)
    
    
@api_view(["POST"])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Driver_management(request):
    
        data = request.data
        
        try:
            driver = DriverData.objects.get(id=data["id"])
        except CustomUser.DoesNotExist:
            return Response({"error": "Driver not valid"}, status=status.HTTP_404_NOT_FOUND)
        
        if data['status']=='active':
            
            driver.request = data['status']
            driver.save()  
            subject = "Caboo Cab Driver Request Verification"
            message = (
                "Congratulations! Your request has been successfully accepted. "
                "Welcome to our community!"
            )
            
        elif data['status'] == 'decline':
            driver.request = data['status']
            driver.dicline_reason = data ['reason']
            driver.comments = data['comments']
            driver.save()  

            subject = "Caboo Cab Driver Request Verification"
            message = (f"We regret to inform you that your request has been declined. "
            f"The reason provided is: {data['comments']}.")
        
        serializer = DriverDataSerializer(driver, data=request.data, partial=True)
        if serializer.is_valid():
            
            from_email = 'akkushahin666@gmail.com'
            recipient_list = ["akkushahin666@gmail.com"]
            result = send_email_task.delay(subject, message, from_email, recipient_list)
            response = task_status(result.id)
            if response.status_code == 200:
              return Response({"success": f"Status update successfully"}, status=status.HTTP_200_OK)
            return Response({'error': "Email sending failed. Please try again later."})
        
        return Response({'error':serializer.errors})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Get_AllTrips(request):
    
    try:
        page_number = request.GET.get('page',1)
        trips = TripDetails.objects.all().order_by('-id')
        page_size = 2
      
        if trips and page_number != 'all':
            
            try:
                
               paginator = Paginator(trips,page_size)
               page = paginator.page(page_number)
               serializer = AllRidesSerializer(page,many=True)
               return Response({ "trips_data":serializer.data,
                              'total_pages': paginator.num_pages,
                              'current_page': page_number,
                              'total_items': paginator.count
                                })
               
            except Exception as e: 
                return Response({"detail": "Page not found."}, status=404)
            
        elif(trips and page_number == 'all'):
            
            serializer = AllRidesSerializer(trips,many=True)
            return Response(serializer.data)
        
    except Exception as e:
        return Response(f"error {e}")
    
@api_view(['POST'])
@permission_classes([IsAuthenticated,RoleBasedPermission])
def Coupon_Management(request):
    
    
    data = request.data
    if data:
        try:
            coupon_data={
            'code':data.get('couponCode'),
            'type':data.get('couponType'),
            'discount':data.get('discount'),
            'max_amount':data.get('maxAmount'),
            'image':data.get('image'),
            'start_date':data.get('startDate'),
            'end_date':data.get('expireDate'),
            'status':data.get('isActive')
                }  
            
            print(coupon_data,'coupon data')
            serializer = CouponSerializer(data=coupon_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"coupon created successfully"},status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors,'error ')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"error coupon {e}")
            return Response ({'error': str(e)},status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error':'data not fount'},status=status.HTTP_404_NOT_FOUND)
    
    
    
    