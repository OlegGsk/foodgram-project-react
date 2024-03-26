from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import FollowingViewSet

users_router = DefaultRouter()

users_router.register('users', FollowingViewSet)


urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')), ]
