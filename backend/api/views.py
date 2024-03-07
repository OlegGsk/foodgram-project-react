from api.serializers import CustomCreateUserSerializer, CustomUserSerializer
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = PageNumberPagination
    # permission_classes = (permissions.AllowAny,)
    # queryset = User.objects.all()
    # # serializer_class = CustomUserSerializer
    # pagination_class = PageNumberPagination
    # http_method_names = ('get', 'post')
    # # filter_backends = [filters.SearchFilter]
    # # lookup_field = 'username'
    # # search_fields = ['username']

    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return CustomCreateUserSerializer
    #     if self.action == 'list' or self.action == 'retrieve':
    #         serializer = CustomUserSerializer
    #         return serializer
    #     return CustomUserSerializer