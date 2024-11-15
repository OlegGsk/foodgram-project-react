from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Follow
from users.serializers import FollowGetSerializer, FollowPostSerializer

User = get_user_model()


class FollowingViewSet(UserViewSet):
    """Получение информации о подписках, создание и удаление подписок."""
    def get_permissions(self):
        if self.action == 'me':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            serializer_class=FollowGetSerializer,
            permission_classes=[permissions.IsAuthenticated],
            )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            serializer_class=FollowPostSerializer,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscribe(self, request, id):
        if not User.objects.filter(id=id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data='Пользователь не найден')

        author = get_object_or_404(User, id=id)
        serializer = self.get_serializer(data=request.data)

        if request.method == 'POST':
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save(user=self.request.user, author=author)
            except IntegrityError:
                return Response('Такая подписка уже существует',
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=self.request.user,
                                         author=author).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data='Такой подписки не существует')
            # serializer.is_valid(raise_exception=True)
            Follow.objects.filter(user=self.request.user,
                                  author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
