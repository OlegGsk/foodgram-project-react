from django.contrib.auth import get_user_model
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from users.serializers import FollowSerializer, FollowingGetSerializer
from django.db.models import Exists, Subquery, OuterRef
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
    # http_method_names = ['get', 'post', 'delete']
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


    @action(detail=False, methods=['get'],
            pagination_class=LimitOffsetPagination)
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowingGetSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


    @action(detail=True, methods=['post', 'delete'],
            serializer_class=FollowSerializer)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        serializer = self.get_serializer(data=request.data)
        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save(user=self.request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


# class FollowingGetViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = FollowingGetSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = LimitOffsetPagination
#     queryset = Follow.objects.all()
#     http_method_names = ['get']
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['user__username', 'author__username']

    # def get_queryset(self):
    #     user = self.request.user
    #     return Follow.objects.filter(user=user).select_related('author').annotate(
    #         recipes=
