from pathlib import Path
import os
from datetime import timedelta
import pymysql
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-i^7sr8m#lpk!a816v3vfm&!mj+v-*4*n5l=-ko9ehjhupg^t55"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600  

ALLOWED_HOSTS = ["*"] 


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "storages",
    "django_quill",
    "mainapp"
    
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # "mainapp.middleware.APIKeyMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  
    # "mainapp.middleware.VerifyAuthTokenMiddleware", 
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "mainapp.middleware.JWTAuthenticationMiddleware",
]

ROOT_URLCONF = "TalentMitra.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR,"templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "TalentMitra.wsgi.application"





# #localy use data base gcloud this is confogure

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'itn-db-hr-email',      # Replace with your actual DB name
#         'USER': 'raj.gupta@intechnative.com',      # Replace with your DB username
#         'PASSWORD': r'6E"(P^\,4KrC/?$E',  # Replace with your DB password
#         'HOST': '127.0.0.1',         # The proxy forwards to localhost
#         'PORT': '1234',
        
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'itn-db-hr-email',
#         'USER': 'raj.gupta@intechnative.com',
#         'PASSWORD': r'6E"(P^\,4KrC/?$E',
#         'HOST': '127.0.0.1',
#         'PORT': '1234',
#     },
#     'secondary': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'itn-db-hr1-dev',
#         'USER': 'dev.singh',
#         'PASSWORD': r'm*Q#{}=~dP3:C:3x',
#         'HOST': '127.0.0.1',
#         'PORT': '1234',  
#     }
# }



# #connection database in googlecloud database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'itn-db-hr-email',      # Replace with your actual DB name
#         'USER': 'raj.gupta@intechnative.com',      # Replace with your DB username
#         'PASSWORD': r'6E"(P^\,4KrC/?$E',  # Replace with your DB password
#          'HOST': '',         # The proxy forwards to localhost
#         'PORT': '',
#         'OPTIONS': {
#             'unix_socket': os.getenv('DB_SOCKET_PATH','/cloudsql/itn-hr-dev:asia-south2:itn-db-hr-dev1')
#         },
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'itn-db-hr-email',
        'USER': 'raj.gupta@intechnative.com',
        'PASSWORD': r'6E"(P^\,4KrC/?$E',
        'HOST': 'localhost',
        'OPTIONS': {
            'unix_socket': os.getenv('DB_SOCKET_PATH','/cloudsql/itn-hr-dev:asia-south2:itn-db-hr-dev1'),
            'charset': 'utf8mb4',
        },
    },
    'secondary': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'itn-db-hr1-dev',
        'USER': 'dev.singh',
        'PASSWORD': r'm*Q#{}=~dP3:C:3x',
        'HOST': 'localhost',
        'OPTIONS': {
            'unix_socket': os.getenv('DB_SOCKET_PATH','/cloudsql/itn-hr-dev:asia-south2:itn-db-hr-dev1'),
            'charset': 'utf8mb4',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

# TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True
TIME_ZONE = 'UTC'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '/media/')



# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "rajendradevloperofficial@gmail.com"
EMAIL_HOST_PASSWORD = "flov mjto qtjf cnwr"
DEFAULT_FROM_EMAIL = ""

from datetime import timedelta

SECRET_KEY = "MYnameIsDEvsiNgH2323637ruyfy3d7dfdf37f3d7f27df73fdcbhevcuyygcue3tuc"





# ✅ CORS Configuration (Allow frontend requests)
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = ["http://localhost:5173",]  # Only allow frontend



# ✅ CSRF & Session Settings (Security)
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173",]
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
# ✅ Django REST Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],  
}


# TIME_ZONE = "Asia/Kolkata"
# USE_TZ = True


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)  

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGS_DIR, "app.log"),  
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],  
        "level": "DEBUG",
    },
}



CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
    "x-csrftoken",
]


API_KEY = os.getenv("API_KEY")

from google.oauth2 import service_account

# Base Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}



# Google Cloud Storage settings
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_BUCKET_NAME = "itn-hr-dev-storage"
GS_BUCKET_NAME_IMG = "itn-public-images"
# GS_DEFAULT_ACL = "publicRead"  # Optional: Adjust permissions as needed
GS_LOCATION = "recruiter_resume"
GEMINI_API_KEY = "AIzaSyC423CfVQgmt2kxdCqyOC0nksKURToNVDs"

# Google Credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"F:\TalentMitra\TalentMitra\credentials.json"






# settings.py (or separate config)
import vertexai
vertexai.init(project="your-gcp-project-id", location="us-central1")





import os
from django.db import connection

def test_connection(request):
    print("Database host:", connection.settings_dict.get('HOST'))
    return HttpResponse("Host printed in logs")
