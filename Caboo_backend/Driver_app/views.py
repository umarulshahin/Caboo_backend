from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from User_app.models import *
from Authentication_app.models import *
from Driver_app.serializer import *
from rest_framework.permissions import IsAuthenticated
from User_app.serializer import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Driver_Data(request):
    
    data = request.GET.get('id', None)
    try:
        
        user=CustomUser.objects.get(email=data)
        driver=DriverData.objects.filter(customuser=user.id).prefetch_related('customuser')
    except :
        return Response({"error":"driver data not done "})

    serializer=DriverDataSerializer(driver,many=True)
    return Response(serializer.data)
     
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def Driver_Status(request):
    data=request.data
    data=dict(data)
    print(data['current_Status'][0],"yes working")
    email=data['customuser[email]'][0]
    try:
        
        user=CustomUser.objects.get(email=email)
        driver=DriverData.objects.filter(customuser=user.id).first()
    except :
        return Response({"error":"driver data not done "})
    update_data = {
            'current_Status': data['current_Status'][0]
        }
    serializer=DriverDataSerializer(driver,data=update_data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Tripdetails(request):
    
    try:
        driver_id = request.GET.get('id')
        trips = TripDetails.objects.filter(driver=driver_id).order_by('-id')
        if trips:
            serializer =AllRidesSerializer(trips,many=True)
            
            return Response(serializer.data)
        return Response('Trips not availabel')
    except Exception as e:
        return Response(f'error trip details {e}')
   
    
