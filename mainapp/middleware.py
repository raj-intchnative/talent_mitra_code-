# mainapp/middleware.py
import logging
from django.http import JsonResponse
from .models import APIKey

logger = logging.getLogger(__name__)

class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the incoming headers
        logger.info(f"Received Headers: {dict(request.headers)}")

        api_key = request.headers.get("X-API-KEY")

        if api_key:
            logger.info(f"Received API key: {api_key[:5]}... (masked)")
        else:
            logger.warning("No valid API key found in headers.")

        if not api_key:
            return JsonResponse({"message": "Unauthorized: No API Key provided."}, status=401)

        if not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return JsonResponse({"message": "Unauthorized: Invalid API Key."}, status=401)

        return self.get_response(request)

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip the authentication for login and public endpoints
        if request.path.startswith("/api/login/"):
            return self.get_response(request)

        # Get the token from cookies
        token = request.COOKIES.get('token')
        print(f"Token from cookies: {token}")

        if not token:
            return JsonResponse({"message": "Unauthorized: No token provided."}, status=401)

        try:
            # Decode the token using the secret key
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(username=payload['username'])
            request.user = user  # Add user to request object for later use
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token has expired."}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid token."}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"message": "User not found."}, status=401)

        return self.get_response(request)


import jwt
import base64
import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# Environment Variables
JWT_SECRET = os.getenv("JWT_SECRET", "JWT_SECRET")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "ENCRYPTION_KEY").encode()
IV_LENGTH = 16

def decrypt_token(encrypted_token):
    try:
        iv, encrypted_text = encrypted_token.split(":")
        iv = base64.b64decode(iv)
        encrypted_text = base64.b64decode(encrypted_text)
        
        cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_padded = decryptor.update(encrypted_text) + decryptor.finalize()
        decrypted = decrypted_padded.rstrip(b"\x00").decode()  # Remove padding
        return decrypted
    except Exception as e:
        print("Decryption error:", str(e))
        return None

class VerifyAuthTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        encrypted_token = request.COOKIES.get("auth_token")
        if not encrypted_token:
            return JsonResponse({"message": "Unauthorized: No token provided."}, status=401)

        try:
            token = decrypt_token(encrypted_token)
            if not token:
                raise jwt.InvalidTokenError("Decryption failed")

            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            user_ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
            user_agent = request.META.get("HTTP_USER_AGENT")

            if decoded.get("userIp") != user_ip or decoded.get("userAgent") != user_agent:
                return JsonResponse({"message": "Session hijacking detected. Login required."}, status=401)

            request.user_data = decoded
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Token expired."}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Invalid or expired token."}, status=401)




import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.COOKIES.get("token")
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                request.user = payload
            except jwt.ExpiredSignatureError:
                return JsonResponse({"message": "Token expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"message": "Invalid token"}, status=403)
