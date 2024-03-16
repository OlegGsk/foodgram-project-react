from django.contrib.auth import get_user_model
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from users.serializers import FollowSerializer, FollowingGetSerializer
from django.db.models import Exists, Subquery
from rest_framework.decorators import action
from djoser.views import UserViewSet
from users.models import Follow
from recipes.models import Recipe
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


User = get_user_model()


class FollowingViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = PageNumberPagination
    queryset = Follow.objects.all()
    lookup_field = 'id'
    http_method_names = ['post', 'delete']
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'author__username']

    def perform_create(self, serializer):
        user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        serializer.save(user=user, author=author)

    def get_object(self):
        user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        return get_object_or_404(Follow, author=author, user=user)


class FollowingGetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowingGetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    queryset = Follow.objects.all()
    http_method_names = ['get']
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['user__username', 'author__username']

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)
