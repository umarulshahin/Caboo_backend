from django.urls import re_path
from . import consumers
from . import Chat_consumer

websocket_urlpatterns = [
    re_path(r'ws/driverlocation/(?P<user_id>\w+)/$', consumers.LocationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<roomId>\d+)/$', Chat_consumer.ChatConsumer.as_asgi()),

]