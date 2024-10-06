
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


CustomUser = get_user_model()

@database_sync_to_async
def get_user(token_key):
    try:
        access_token = AccessToken(token_key)
        user = CustomUser.objects.get(id=access_token['user_id'])
        return user
    
    except (CustomUser.DoesNotExist, KeyError):
        print("User not found or 'user_id' not in token")
        return AnonymousUser()

    except TokenError as e:
        # Handle invalid or expired token
        print(f"Token error: {e}")
        return AnonymousUser()

    except InvalidToken as e:
        print(f"Invalid token: {e}")
        return AnonymousUser()

    except Exception as e:
        # Catch any other exceptions
        print(f"Unexpected error during token validation: {e}")
        return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        token_key = None
        if 'token=' in query_string:
            token_key = query_string.split('token=')[1]

        # If a token is found, get the user
        if token_key:
            scope['user'] = await get_user(token_key)

        return await super().__call__(scope, receive, send)
