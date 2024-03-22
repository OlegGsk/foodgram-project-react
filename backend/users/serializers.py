import re

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class AlterRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ("__all__",)


class CustomCreateUserSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')
        read_only_fields = ('id',)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me"'
            )
        if not bool(re.match(r'^[\w.@+-]+$', value)):
            raise serializers.ValidationError(
                'Некорректные символы в username')
        return value


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='author.recipes.count', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.PrimaryKeyRelatedField(source='author.id', read_only=True)
    email = serializers.EmailField(source='author.email', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='author.last_name',
                                      read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes_count', 'is_subscribed', 'recipes')
        read_only_fields = ('__all__',)

    def validate(self, data):
        user = self.context['request'].user
        request = self.context['request']
        author = self.context['author']

        if request.method == 'POST':
            if author == user:
                raise serializers.ValidationError(
                    'Вы не можете подписаться на себя')
            if Follow.objects.filter(user=user, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя')
        if request.method == 'DELETE' and not Follow.objects.filter(
                user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы не подписаны на этого пользователя')
        return data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=obj.author).exists()

    def get_recipes(self, obj):
        user = self.context['request'].user
        request = self.context.get('request')
        if user.is_anonymous:
            return []
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if not recipes_limit:
            return AlterRecipeSerializer(recipes, many=True).data
        return AlterRecipeSerializer(recipes[:int(recipes_limit)],
                                     many=True).data
