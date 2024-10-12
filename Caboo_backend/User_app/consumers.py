from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps
from channels.db import database_sync_to_async
import json
from math import radians, sin, cos, sqrt, atan2
import random
import asyncio
from django.db.models import *
import traceback
from django.utils import timezone

class LocationConsumer(AsyncJsonWebsocketConsumer):
    user_data = {}
    drivers_distance = []
    trip_id = None
    active_drivers = set()
    
    @sync_to_async
    def driver_rating(self,driver):
        from User_app.models import TripDetails
        
        try: 
            rating = TripDetails.objects.filter(driver=driver).aggregate(total=Avg('rating'))
            print(rating['total'],'rating avg')  
            return rating['total']     
        except Exception as e:
            print(f'driver rating error {e}')
    
    @sync_to_async
    def get_tripdata(self,trip_id):
       from User_app.models import TripDetails
       
       try:
           trip_data=TripDetails.objects.filter(id=trip_id).first()
           print(trip_data,"trip data get")
           data={
               "user_id":trip_data.user_id,
               "driver_id":trip_data.driver_id
           }
           return data
       except Exception as e:
           print(f"get trip data error {e}")  
      
    
    @sync_to_async
    def RideStatus(self,user):
        from Authentication_app.models import CustomUser
        try:
            return CustomUser.objects.filter(id=user,ride=False).first()
        except Exception as e:
            print(f"Ride status error {e}")
    
    @sync_to_async
    def updateRide(self,user_id,driver_id,data):
        
        from User_app.serializer import UserSerializer,WalletSerializer
        from Authentication_app.models import CustomUser
        from User_app.models import UserWallet
     
        try:
           if user_id and driver_id:
                user = CustomUser.objects.get(id=user_id)
                driver = CustomUser.objects.get(id=driver_id)
              
                if user and driver:
                    if 'wallet' in data:
                        pay_amount = int(data['wallet'])
                        data['wallet']=int(user.wallet) - int(data['wallet'])
                        
                    userserializer = UserSerializer(user, data, partial=True)
                    if userserializer.is_valid():
                        userserializer.save()
                    else:
                        print('User serializer error:', userserializer.errors)
                        return False
                
                ride = data.get('ride', {})
                driverserializer = UserSerializer(driver,{'ride': ride}, partial=True)
                if driverserializer.is_valid():
                    driverserializer.save()
                else:
                    print('Driver serializer error:', driverserializer.errors)
                    return False
                
                # Handle wallet transaction if 'wallet' is in data
                if 'wallet' in data:

                    wallet_data = {
                        "customuser": user.id,
                        "amount": pay_amount,
                        "reason": "Trip payment",
                        "status": "pay"
                    }
                    print(wallet_data,'wallet data')
                    wallet_serializer = WalletSerializer(data=wallet_data)
                    if wallet_serializer.is_valid():
                        wallet_serializer.save()
                    else:
                        print('Wallet serializer error:', wallet_serializer.errors)
                        return False
                
                print('yes working all fine')
                return True
                         
        except Exception as e:
            print(f"update ride error {e}")
       
    
    @sync_to_async
    def Trip_update(self,data,trip_id,coupon_id=0):
        from .serializer import TripSerializer
        from .models import TripDetails,UsedCoupons
        
        print(data,'trip updation is working')
        try:
        
            if 'payment_type' in data:
                update_data = {
                    "payment_type" : data['payment_type'],
                    "status":data['status']
                }
            else:
                update_data={
                    "status":data
                }
                
            trip = TripDetails.objects.filter(id=trip_id).first()
            print(trip,'trip data ')
            serializer = TripSerializer(trip,data=update_data,partial=True)
            if serializer.is_valid():
                serializer.save()
                if coupon_id:
                   print(serializer.data['user'],'user id')
                #    UsedCoupons.objects.create(User_id=serializer.data['user'],Coupon_id=coupon_id)
                
                return "successfully update"

            else:
                print('Trip update error :',serializer.errors)
        except Exception as e:
        
           print(f"error {e}")

    @sync_to_async
    def otp_validate(self,data):
        from .serializer import OTPValidationSerializer
        
        otp_data ={
            'tripOTP':data['Otp_data']['otp'],
            'driver' : data['Otp_data']['driver_id']
        }
        print(otp_data,'otp_data')
        serializer= OTPValidationSerializer(data=otp_data)
        
        if serializer.is_valid():
            return serializer.validated_data
        
        else:
            return {'error':serializer.errors}
        
        
    @sync_to_async
    def Save_trip(self,tripdata):
        from .serializer import TripSerializer
        
        serializer = TripSerializer(data=tripdata)
        if serializer.is_valid():
            serializer.save()
            LocationConsumer.trip_id=serializer.data['id']
            return serializer.data
        else:
            print(serializer.errors ,'yes this error is working')
            return None
    
    @sync_to_async
    def Get_driverdata(self, data):
        print(data, 'call is coming get driver data')
        from Authentication_app.models import CustomUser, DriverData
        
        try:
            return list(DriverData.objects.filter(customuser=data).prefetch_related('customuser'))
        except Exception as e:
            print(f"error get driver {e}")
            return None
            
    @sync_to_async
    def serialize_driver_data(self, driver):
        
        from Driver_app.serializer import DriverDataSerializer
        
        return DriverDataSerializer(driver, many=True).data
    
    async def Ride_Acceptance(self, data):
        try:
            print('yes ride accpet is working')
            userData = data['ride_data']['userRequest']
            driverId = data['driver_id']
            userId = data['ride_data']['userRequest']['user_id'] 
            service = data['ride_data']['userRequest']['type']
            
            OTP = str(random.randint(1000, 9999))

            if userId and driverId and data :
                print("yes working id data",data)
                print(data['driver_id'],'driver id in acceptence')
                LocationConsumer.driver_id=data['driver_id']
                tripdata = {
                    'user': userId,
                    'driver': driverId,
                    'location': userData['places']['location'],
                    'destination': userData['places']['destination'],
                    'distance': userData['distance']['distance']['text'],
                    'duration': userData['distance']['duration']['text'],
                    'amount': userData['price'],
                    'tripOTP': OTP,
                    'service_type' : service,
                    'status': 'pending'
                }
                
                save_trip = await self.Save_trip(tripdata)

                if save_trip:
                    driverdata = await self.Get_driverdata(save_trip['driver'])

                    if driverdata:
                        print('yes diver data is working ')
                        driver = await self.serialize_driver_data(driverdata)
                        print(driver,'dirver after also working')
                        if driver:
                            print('yes it is working ',driver)
                            data={
                                    'ride':True
                                }
                            result=await self.updateRide(userId,driverId,data)
                            if result:
                                return {
                                        'trip_data': save_trip,
                                        'driver_data': driver
                                    }
                    else:
                        print('No driver data found')
                else:
                    print('Failed to save trip')
            else:
                print('Ride Acceptance Error: User or Driver is None')

        except Exception as e:
            print(f"Ride Acceptance Error: {e}")
            return None
        
    @database_sync_to_async
    def save_driver_location(self, driver_id, location, user_id):
        DriverLocation = apps.get_model('User_app', 'DriverLocation')
        
        try:
            DriverLocation.objects.create(
                user_id=user_id,
                driver_id=driver_id,
                location=dict(location)
                
            )
        except Exception as e:
            print(f'Driver location saving error: {e}')

    @sync_to_async
    def get_active_drivers(self, vehicle_type):
        CustomUser = apps.get_model('Authentication_app', 'CustomUser')
        DriverData = apps.get_model('Authentication_app', 'DriverData')
        try:
            return list(DriverData.objects.filter(
                Vehicle_type=vehicle_type,
                current_Status=True,
                customuser__ride=False
            ).values_list('customuser_id', flat=True))
            
        except Exception as e:
            print(f"Error in get_active_drivers: {e}")
            return []
        
        
    @sync_to_async
    def uservalidate(self,user_id):
        CustomUser = apps.get_model('Authentication_app', 'CustomUser')
        try:
            return CustomUser.objects.filter(id=user_id,is_active=True).exists()
        
        except Exception as e:
            print(f'uservalidation error  {e}') 
    
    # @sync_to_async
    # def Current_ride_check(self,user_id):
    #     Trips = apps.get_model('User_app', 'TripDetails')
    #     from django.db.models import Q
    #     from .serializer import AllRidesSerializer

    #     try:
            
    #         result= Trips.objects.filter((Q(driver_id=user_id) | Q(user_id=user_id)) & Q(status="pending")).order_by('-id').first() 
    #         if result:       
    #             return AllRidesSerializer(result).data
    #     except Exception as e :
         
    #      print(f"current ride check error {e}")
    @sync_to_async 
    def get_coupons(self,user_id):
        Coupons = apps.get_model('Admin_app', 'Coupons','UsedCoupons')
        UsedCoupons = apps.get_model('User_app', 'UsedCoupons')
        from Admin_app.serializer import CouponSerializer

        
        try:
            today = timezone.now().date()
            available_coupons = Coupons.objects.filter(
            status=True,
            end_date__gte=today
            ).exclude(
                usedcoupons__User_id=user_id  
            )

            print(available_coupons, 'available coupons')
            if available_coupons:
               serializer = CouponSerializer(available_coupons,many=True)
            return serializer.data
            
        except Exception as e:
            
           print(f"error get coupon {e}")
    
    
    async def connect(self):
        
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        await self.accept()
        
        user_type = await self.get_user_type(self.user_id)
        print(f'Connection established for {user_type} with ID {self.user_id}')
            
        
        if user_type == 'driver':
            await self.channel_layer.group_add('all_drivers', self.channel_name)
        else:
            await self.channel_layer.group_add('all_users', self.channel_name)
            
        if user_type and self.user_id:
            await self.channel_layer.group_add(f'{user_type}_{self.user_id}', self.channel_name)
            print(f'Added to group: {user_type}_{self.user_id}')
            result = await self.uservalidate(self.user_id)
            print(result,'result of the user validation ')
            if not result:
                
                 await self.channel_layer.group_send(
                            f'{user_type}_{self.user_id}', 
                            {
                                'type': 'BlockNotification',
                                'status': 'Your account has been blocked',
                                'message': 'Your account has been blocked. Please contact our customer service.',
                            }
                        )
            # current_ride = await self.Current_ride_check(self.user_id)
            # print(current_ride,'current ride')
            # if current_ride:
                
            #      await self.channel_layer.group_send(
            #                 f'{user_type}_{self.user_id}', 
            #                 {
            #                     'type': 'SuccessNotification',
            #                     'status': 'pending ride',
            #                     'message': current_ride,
            #                 }
            #             )
                
    async def disconnect(self, close_code):
        # Remove from all groups
        await self.channel_layer.group_discard(f'user_{self.user_id}', self.channel_name)
        await self.channel_layer.group_discard(f'driver_{self.user_id}', self.channel_name)
        await self.channel_layer.group_discard('all_drivers', self.channel_name)
        await self.channel_layer.group_discard('all_users', self.channel_name)


            
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            print(data,'receved data')
            
            
            if 'userRequest' in data and 'type' in data['userRequest']:
                
                LocationConsumer.drivers_distance.clear()
                LocationConsumer.user_data.clear()
                LocationConsumer.active_drivers.clear()
                
                user_id = data['userRequest']['user_id']
                user_type = await self.get_user_type(user_id)
                if user_type == 'user':
                    result = await self.RideStatus(user_id)
                    if result:
                        await self.handle_user_request(data)
                    else:
                        await self.channel_layer.group_send(
                            f'user_{user_id}', 
                            {
                                'type': 'SuccessNotification',
                                'status': 'User already in a ride',
                                'message': 'User already in a ride. First finish current ride then try again.',
                            }
                        )
                else:
                    print(f"Ride request received from a driver (ID: {user_id}). Ignoring.")
                    
            elif 'Driverlocation' in data:
                try:
                    driver_id = data.get('id')
                    location = data.get('Driverlocation')
                    user_id = data.get('user_id')
                    print(user_id,'user id in driver location')
                    if driver_id and location:
                        await self.save_driver_location(driver_id, location,user_id)
                except Exception as e:
                    print(f"driver location {e}")
                
            elif 'rideRequestResponse' in data:
                
                if data['rideRequestResponse'] == 'accepted':
                    
                    print('accept working')
                    result = await self.Ride_Acceptance(data)
                    print(result,'accept result')

                    if result:
                        id = result['trip_data']['id']

                        driver_id = result['trip_data']['driver']
                        print(driver_id,'request notification for driver')
                        
                        LocationConsumer.drivers_distance.clear()
                        
                        user_id = result['trip_data']['user']
                        rating = await self.driver_rating(driver_id)
                        
                        print(id,'trip id ')

                        print(driver_id,'driver id ')
                        print(user_id,'user id ')
                        await self.channel_layer.group_send(
                            f'driver_{driver_id}',
                            {
                                'type': 'notify_driver',
                                'trip_id' : id
                            }
                        )
                        
                        await asyncio.sleep(3)  
                        
                        print(id,'trip id ')
                        await self.channel_layer.group_send(
                            f'user_{user_id}', 
                            {
                                'type': 'notify_user',
                                'user_data': data,
                                'tripdata' : result,
                                'trip_id' : id,
                                'rating' : rating
                            }
                        )
                        
                       
                    else:
                        print("error result is empty")
                  
                elif data['rideRequestResponse'] == 'declined':
                    if LocationConsumer.drivers_distance:
                        print(data,'decline request')
                        value = list(LocationConsumer.drivers_distance.pop(0))
                        await self.channel_layer.group_send(
                            f'driver_{value[0]}',
                            {
                                'type': 'Ride_request',
                                'driver_id': value[0],
                                'user_data': LocationConsumer.user_data
                            }
                        )
                    else:
                        print('Driver not available')
                        user_id=data['user_data']['userRequest']['user_id']
                        if user_id:
                           await self.notify_user_no_drivers(user_id)
                        else:
                            print('user id not available')
                        
            elif 'Otp_data' in data:
                
                result = await self.otp_validate(data)
                trip_data = await self.get_tripdata(data['trip_id'])
                                
                if 'tripOTP' in result and 'driver' in result and trip_data:
                    
                    if 'user_id' in trip_data and 'driver_id' in trip_data:
                    
                            await self.channel_layer.group_send(
                                    f"user_{trip_data['user_id']}", 
                                    {
                                        'type': 'SuccessNotification',
                                        'status': 'OTP_success',
                                        'message': 'OTP validation succeeded. Trip is confirmed.',
                                    }
                                )
                            
                            
                            await self.channel_layer.group_send(
                            f"driver_{trip_data['driver_id']}",
                            {
                                
                                'type' : 'SuccessNotification',
                                'status': 'OTP_success',
                                'message': 'OTP validation succeeded. You can start the trip.',

                            }  
                            )
                    else:
                        
                        print('error otp data user id or driver id is missing ')
                    
                elif 'error' in result:
                    id=data['Otp_data']['driver_id']
                    await self.channel_layer.group_send(
                       f'driver_{id}',
                       {
                        'type' : 'OTP_faild'
                       } 
                    )
                    
            elif 'ride_complete' in data:
                
                result = await self.Trip_update("completed",data['trip_id'])
                trip_data = await self.get_tripdata(data['trip_id'])
                print(trip_data,'trip completed')
                coupons = await self.get_coupons(trip_data['user_id'])
                
                if result == 'successfully update' and trip_data:

                    await self.channel_layer.group_send(
                            f"user_{trip_data['user_id']}", 
                            {
                                'type': 'SuccessNotification',
                                'status': 'Trip complete',
                                'message': coupons,
                            }
                        )
                
            elif 'userRequest' in data and 'payment_type' in data['userRequest']:
                                
                    trip_data = await self.get_tripdata(data['userRequest']['trip_id'])

                    if data['userRequest']['payment_type']=='cashinhand' and trip_data:
                        print(data,'cash in hand ')
                        await self.channel_layer.group_send(
                        f"driver_{trip_data['driver_id']}",
                        {
                            
                            'type' : 'SuccessNotification',
                            'status': 'Payment verification',
                            'message': data,
                            
                        }  
                        )
                    elif data['userRequest']['payment_type'] =='wallet' and trip_data:
                        
                          amount = data['userRequest']['amount']
                          result = await self.Trip_update({'payment_type' : data['userRequest']['payment_type'],'status': 'completed'},data['userRequest']['trip_id'])
                          if result == 'successfully update' and amount:
                                data = {
                                'ride':False,
                                'wallet':amount
                                }
                                update = await self.updateRide(trip_data['user_id'],trip_data['driver_id'],data) 
                                if update:
                                    await self.channel_layer.group_send(
                                        f"driver_{trip_data['driver_id']}",
                                        {
                                            
                                            'type' : 'SuccessNotification',
                                            'status': 'payment completed',
                                            'message': data,
                                            
                                        }  
                                    )       
                                    
                                    await asyncio.sleep(1)  

                                    await self.channel_layer.group_send(
                                        f"user_{trip_data['user_id']}", 
                                        {
                                            'type': 'SuccessNotification',
                                            'status': 'payment completed',
                                            'message': 'Trip complete successfylly',
                                        }
                                    )       
                                    
                                    
                    elif data['userRequest']['payment_type'] =='razorpay' and trip_data:
                        
                        amount = data['userRequest']['amount']
                        result = await self.Trip_update({'payment_type' : data['userRequest']['payment_type'],'status': 'completed'},data['userRequest']['trip_id'])
                        if result == 'successfully update' and amount:
                                data = {
                                'ride':False,
                                }
                                update = await self.updateRide(trip_data['user_id'],trip_data['driver_id'],data) 
                                if update:
                                    await self.channel_layer.group_send(
                                        f"driver_{trip_data['driver_id']}",
                                        {
                                            
                                            'type' : 'SuccessNotification',
                                            'status': 'payment completed ',
                                            'message': data,
                                            
                                        }  
                                    )       
                                    
                                    await asyncio.sleep(3)  

                                    await self.channel_layer.group_send(
                                        f"user_{trip_data['user_id']}", 
                                        {
                                            'type': 'SuccessNotification',
                                            'status': 'payment completed',
                                            'message': 'Trip complete successfylly',
                                        }
                                    )       
                                
                    else:
                        print('payment reach user side error')
                        
            elif 'payment received' in data:
                print(data,'payment recevid')
                coupon_id=0
                if 'applyoffer' in data:
                    coupon_id =data['applyoffer']['id']
                    print(coupon_id,'coupon_id')
                result = await self.Trip_update({'payment_type' : data['payment received'],'status': 'completed'},data['trip_id'],coupon_id)
                trip_data = await self.get_tripdata(data['trip_id'])
                if result == 'successfully update' and trip_data:
                    data = {
                    'ride':False
                    }
                    update = await self.updateRide(trip_data['user_id'],trip_data['driver_id'],data)
                    if update:
                        await self.channel_layer.group_send(
                                f"user_{trip_data['user_id']}", 
                                {
                                    'type': 'SuccessNotification',
                                    'status': 'payment completed',
                                    'message': 'Trip complete successfylly',
                                }
                            )
                    else:
                        print('trip update error in payment received')
                        
            elif 'usertripcancel' in data:
                
                trip_id=data['usertripcancel']['trip_id']
                result = await self.Trip_update("cancelled",trip_id)
                if result == 'successfully update':
                    print('yes its working inside ')
                    ids= await self.get_tripdata(trip_id)
                    if ids:
                        data = {
                            'ride':False
                        }
                        update = await self.updateRide(ids['user_id'],ids['driver_id'],data)
                        print(update,'updated data')
                        if update:
                            await self.channel_layer.group_send(
                            f"driver_{ids['driver_id']}",
                            {
                                
                                'type' : 'SuccessNotification',
                                'status': 'Trip cancel',
                                'message': 'User want cancel this trip',
                                
                            }  
                            )
                    else:
                        print('trip update error user trip cancel')
                    
            elif 'drivertripcancel' in data:
               
                trip_id=data['trip_id']
                result = await self.Trip_update("cancelled",trip_id)
                
                if result == 'successfully update':
                    ids= await self.get_tripdata(trip_id)
                    data = {
                            'ride':False
                        }
                    update = await self.updateRide(ids['user_id'],ids['driver_id'],data)
                    if update:
                        await self.channel_layer.group_send(
                                f"user_{ids['user_id']}", 
                                {
                                    'type': 'SuccessNotification',
                                    'status': 'Trip cancel',
                                    'message': 'Driver want cancel this trip',
                            
                                }
                            )                
                    else:
                        print("error trip updation error in driver cancel")
                        
            elif 'paymentdetails' in data:
                
                print('yes payment coming')

            else:
                print(f"Received unknown data format: {data}")
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {text_data}")
        except Exception as e:
            print('yes error is woring')
            print(f"Error in receive: {e}")
            traceback.print_exc()


        
    async def handle_user_request(self, data):
        
        user_id = data['userRequest']['user_id']
        vehicle_type = data['userRequest'].get('type')
        LocationConsumer.user_data = data

        LocationConsumer.active_drivers = await self.get_active_drivers(vehicle_type)
        print(LocationConsumer.active_drivers,'active drivers')
        # Request locations from all active drivers 
        await self.request_driver_locations(user_id)

        # Wait for a short time to allow drivers to respond
        await asyncio.sleep(5)

        # Process received locations and find the nearest driver
        await self.process_driver_locations(user_id)
        
    async def request_driver_locations(self,user_id):
        print('reques driver is working ')
        for driver_id in LocationConsumer.active_drivers:
            await self.channel_layer.group_send(
                f'driver_{driver_id}',
                {
                    'type': 'request_location',
                    'user_id': user_id
                }
            )
            
            
    async def process_driver_locations(self, user_id):
        
        DriverLocation = apps.get_model('User_app', 'DriverLocation')
        user_location = LocationConsumer.user_data['userRequest']['place_code']['location']
        user_lat = user_location['lat']
        user_lng = user_location['lng']

        print(type(user_id),'type user id ')
        for driver_id in self.active_drivers:
            print(type(driver_id),'driver id ')
            try:
                location = await database_sync_to_async(DriverLocation.objects.filter(driver_id=int(driver_id),user_id=int(user_id)).latest)('timestamp')
                
                if location:
                    latitude = location.location.get('latitude')
                    longitude = location.location.get('longitude'
                                                  )
                    distance = await self.distance_calculation(
                        user_lat, user_lng, 
                       latitude, longitude
                    )
                    print('yes append is working')
                    LocationConsumer.drivers_distance.append((driver_id, distance))
                else:
                    print('error location data is empty ')
                
            except DriverLocation.DoesNotExist:
                print(f"No location found for driver {driver_id}")
            except Exception as e:
                print(f'error in process driver location {e}')
                traceback.print_exc()

        print(LocationConsumer.drivers_distance,'drivers distance')
        if LocationConsumer.drivers_distance:
            LocationConsumer.drivers_distance.sort(key=lambda x: x[1])
            nearest_driver = LocationConsumer.drivers_distance.pop(0)
           
            
            await self.channel_layer.group_send(
            f'driver_{nearest_driver[0]}',
            {
                'type': 'Ride_request',
                'driver_id': driver_id,
                'user_data': LocationConsumer.user_data
            }
        )
            
        else:
            await self.notify_user_no_drivers(user_id)


    async def request_location(self, event):
        print(event,'request location is working')
        await self.send(text_data=json.dumps({
                'type': 'location_request',
                'user_id': event['user_id']
            }))
            
    @sync_to_async
    def get_user_type(self, user_id):
        userdata = apps.get_model('Authentication_app', 'CustomUser')
        DriverData = apps.get_model('Authentication_app', 'DriverData')
        try:
            print(f'Determining user type for user ID: {user_id}')
            driver = DriverData.objects.filter(customuser=user_id, current_Status=True).first()
            if driver:
                return 'driver'
            return 'user'
        except Exception as e:
            print(f"Error in get_user_type: {e}")


    async def distance_calculation(self, user_lat, user_lng, driver_lat, driver_lng):
        print('yes distance caluclation is working ')
        R = 6371
        dlat = radians(driver_lat - user_lat)
        dlon = radians(driver_lng - user_lng)
        a = sin(dlat / 2) ** 2 + cos(radians(user_lat)) * cos(radians(driver_lat)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance
    

    async def Ride_request(self, event):
        print('yes ride reques is working ')
        await self.send(text_data=json.dumps({
            'type': 'Riding_request',
            'driver_id': event['driver_id'],
            'user_data': LocationConsumer.user_data
        }))
        
    
    async def notify_user(self, event):
        
        print(' yes notify is working')
        await self.send(text_data=json.dumps({
            'type': 'ride_accepted',
            'data': event
        }))


    async def OTP_faild(self,event):
        
        await self.send(text_data=json.dumps({
            
            'type' : 'otp validation faild '
            
        }))
        
    async def notify_user_no_drivers(self, user_id):
        await self.channel_layer.group_send(
            f'user_{user_id}',
            {
                'type': 'SuccessNotification',
                'status': 'No_drivers_available',
                'message': 'No drivers are currently available. Please try again later.',
            }
        )
    async def SuccessNotification(self, event):
        print('yes success notification is working')
        await self.send(text_data=json.dumps({
            'type': event['status'],
            'message': event['message'],
        }))
    
    async def notify_driver(self,event):
        print(event,'driver notify is working')
        await self.send(text_data=json.dumps({
            'type': 'ride_accepted',
            'data': event
        }))
    
    async def BlockNotification(self,event):
        print("block notification is working")
        await self.send(text_data=json.dumps({
            'type': 'block notification',
            'data': event
        }))