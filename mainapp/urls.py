from django.conf import settings
from django.urls import path, include

urlpatterns = [  
    path("api/", include("mainapp.urls")),
]
