from django.db import router
from django.urls import path, include
from users.views import FollowingViewSet
from rest_framework.routers import DefaultRouter

users_router = DefaultRouter()

users_router.register('users', FollowingViewSet,
                      basename='following')


urlpatterns = [
    path('', include(users_router.urls)),
    # path('', include('djoser.urls')),
    # path('users/<int:id>/subscribe/', FollowingViewSet.as_view(
    #     {'post': 'create', 'delete': 'destroy'})),
    # path('users/subscriptions/', FollowingGetViewSet.as_view(
    #     {'get': 'list'}),
        #  name='subscriptions'),
    path('', include('djoser.urls')),
    # path('', include(users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    ]
