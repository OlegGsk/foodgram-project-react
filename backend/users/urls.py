from django.db import router
from django.urls import path, include
from users.views import FollowingViewSet
from rest_framework.routers import DefaultRouter

users_router = DefaultRouter()

users_router.register('users', FollowingViewSet)


urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    ]
