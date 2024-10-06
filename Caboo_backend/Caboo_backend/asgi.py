import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from User_app.routing import websocket_urlpatterns
# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Caboo_backend.settings')

django.setup()

from User_app.Auth_middleware import JwtAuthMiddleware


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        JwtAuthMiddleware(  
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
