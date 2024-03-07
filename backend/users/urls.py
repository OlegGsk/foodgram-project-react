from django.db import router
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from users.views import CustomUserViewSet


router = DefaultRouter()
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    ]
