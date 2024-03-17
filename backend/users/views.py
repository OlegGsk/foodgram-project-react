from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.models import Follow
from users.serializers import FollowingGetSerializer, FollowSerializer

User = get_user_model()


class FollowingViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination
    permissions_class = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['get'],
            serializer_class=FollowingGetSerializer)
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

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
            serializer.is_valid(raise_exception=True)
            Follow.objects.filter(user=self.request.user,
                                  author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
