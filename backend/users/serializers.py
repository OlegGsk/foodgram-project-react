from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomCreateUserSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        read_only_fields = ('id',)


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
