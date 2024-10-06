from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser

        self.user = self.scope['user']
        print(f"{self.user} user in chat")
        if isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return 

        self.roomId = self.scope['url_route']['kwargs']['roomId']
        self.room_name = f'chat_{self.roomId}'
        self.room_group_name = self.room_name 
        
        self.processed_message_ids = set()

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Chat data received: {data}")
      
        message_type = data['type']
        message_id = data.get('message_id') or data.get('messageId')

        if not message_id:
            print("Message ID is missing")
            return

        if message_id in self.processed_message_ids:
            print(f"Duplicate message_id {message_id} ignored")
            return

        self.processed_message_ids.add(message_id)

        if message_type == 'received':
            await self.handle_received_message(data)
        elif message_type == 'sendMessge':
            await self.handle_send_message(data)
        else:
            print(f"Unknown message type: {message_type}")

    async def handle_received_message(self, data):
        user_id = data.get('user_id')
        message_id = data['message_id']
        
        if user_id:
            await self.channel_layer.group_send(
                f'chat_{user_id}',
                {
                    'type': 'delivery_confirmation',
                    'status': 'delivered',
                    'message_id': message_id,
                }
            )
        else:
            print('User ID is missing for received message')

    async def handle_send_message(self, data):
        connect_id = data['connectId']
        message_id = data['messageId']

        await self.channel_layer.group_send(
            f'chat_{connect_id}',
            {
                'type': "chat_message",
                'message': data['message'],
                'user_id': self.roomId,
                'message_id': message_id
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'message_id': event['message_id']
        }))
          
    async def delivery_confirmation(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delivery_status',
            'status': 'delivered',
            'message_id': event['message_id'],
        }))