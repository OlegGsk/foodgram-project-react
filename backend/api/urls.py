from django.db import router
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import TagViewSet

router = DefaultRouter()

router.register('tags', viewset=TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('users.urls'))
    ]
