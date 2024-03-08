# from users.serializers import CustomCreateUserSerializer, CustomUserSerializer
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


# class CustomUserViewSet(UserViewSet):
#     pagination_class = PageNumberPagination
