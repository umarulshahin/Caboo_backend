from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from .serializer import *
from rest_framework import status
from .models import *
from rest_framework.permissions import IsAuthenticated
from  Authentication_app.models import *
import razorpay
from django.conf import settings        
from django.db.models import *
from Driver_app.serializer import *
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
# from django.http import JsonResponse

        
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])    
def Image_Upload(request):
    
    if request.method == "PATCH":
        image = request.FILES.get('image')
        id = request.data.get('id')
        print(image,'image name ')
        if not image:
            return Response({"error": "Image file is required"}, status=400)
        data = {"image": image, "id": id}

        serializer = ImageUploadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        
            return Response({"Success": "Image uploaded successfully"}, status=200)
        return Response({"error": serializer.errors}, status=400)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])    
def GetUser(request):
    print('yes here is working ')
    user = request.user
    data=CustomUser.objects.filter(email=user,is_active=True)
    if data:
        serializer=UserSerializer(data,many=True)
        print(serializer.data,'user side')
        return Response(serializer.data)

    
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def ProfilUpdate(request):
    
    try:
        
        user_id=request.data.get('id')
        user=CustomUser.objects.get(id=user_id,is_active=True)
        if user :
            serializer =UserSerializer(user,request.data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response({"error":serializer.errors})
        
            
        return Response({"error":"User data not get"})
    except Exception as e:
        return Response({'error':e},status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])   
def Payment(request):
    
    try:
      data=request.data
      amount = data
      print(amount,'amount')
      
      secret_key = settings.RAZORPAY_SECRET_KEY  
      public_key = settings.RAZORPAY_PUBLIC_KEY
      
      if int(amount) >0:
          
            client = razorpay.Client(auth=(public_key, secret_key))

            payment = client.order.create({"amount": int(amount) * 100, 
                                        "currency": "INR", 
                                        "payment_capture": "1"})
            print(payment,'payment ')
            return Response(payment)
      return Response({"error": "The minimum amount must be at least ₹1."},status=status.HTTP_400_BAD_REQUEST)
     
    except Exception as e:
        return Response ({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
      
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PaymentSuccess(request):
    
    try:
        user_id = request.data['user'][0]['id']
        amount = request.data['amount']
        if user_id:
            user=CustomUser.objects.get(id=user_id)
            if user:
                data={
                    "customuser":user.id,
                    "amount":int(amount),
                    "reason":"Wallet recharge",
                    "status":"add"
                }
                print(data,'data creation')
                serialize = WalletSerializer(data=data)
                if serialize.is_valid():
                    serialize.save()
                    total = int(user.wallet) + int(amount)
                    
                    userserializer = UserSerializer(user,{'wallet':total},partial=True)
                    if userserializer.is_valid():
                        userserializer.save()
                    
                        return Response({"success":serialize.data})
                    return Response({'error':userserializer.errors})
                return Response({'error':serialize.errors})
            return Response({'error':"user not available"},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"error from payment success {e}")
        return Response({"error":str(e)})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Ridedetails(request):
    
    try:
        user_id = request.GET.get('id')  
        trips = TripDetails.objects.filter(user=user_id).order_by('-id')
        if trips:
            serializer =AllRidesSerializer(trips,many=True)
            return Response(serializer.data)
    except Exception as e:
        print(e,'error ')
        return Response(f'error {e}')
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Walletdetails(request):
     
    try:
        
        user_id = request.GET.get('id')  
        page_number = request.GET.get('page',1)
        print(page_number,'page number')
        page_size = 5
        data=UserWallet.objects.filter(customuser=user_id).order_by('-id')
        if data:
            paginator = Paginator(data,page_size)
            try:
                page = paginator.page(page_number)
            except Exception as e:
                return Response({"detail": "Page not found."}, status=404)
            
            serializer = WalletSerializer(page,many=True)
            return Response({
                'wallet_details': serializer.data,
                'total_pages': paginator.num_pages,
                'current_page': page_number,
                'total_items': paginator.count,
            })    
    except Exception as e:
        
        return Response(f'error {e}')
        
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Review(request):
    try:
        print('pani yaan idh 12')
        data = request.data
        trip = TripDetails.objects.get(id=data['tripId'])
        serializer =TripSerializer(trip,data,partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    except Exception as e:
        return Response(f"error review {e}")
   
