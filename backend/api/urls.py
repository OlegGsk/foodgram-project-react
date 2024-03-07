from django.db import router
from rest_framework.routers import DefaultRouter
from django.urls import path, include


urlpatterns = [
    path('', include('users.urls'))
    ]
