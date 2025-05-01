# decorators.py
import jwt
from django.http import JsonResponse
from django.conf import settings
from functools import wraps

SECRET_KEY = settings.SECRET_KEY

def with_token_info(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        token = request.COOKIES.get("token")
        if not token:
            return JsonResponse({"error": "No token found"}, status=401)

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.role = decoded_token.get("username")
            request.role_id = decoded_token.get("password")
            return func(self, request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

    return wrapper
