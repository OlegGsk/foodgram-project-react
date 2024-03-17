from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=self.context['view'].kwargs.get('id')).exists()


class FollowSerializer(serializers.ModelSerializer):
    recipes = AlterRecipeSerializer(source='author.recipes', many=True,
                                    read_only=True)
    recipes_count = serializers.IntegerField(
        source='author.recipes.count', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.PrimaryKeyRelatedField(source='author.id', read_only=True)
    email = serializers.EmailField(source='author.email', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name', read_only=True)
    last_name = serializers.CharField(source='author.last_name', read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes_count', 'is_subscribed', 'recipes')
        read_only_fields = ('__all__',)

    def validate(self, data):
        user = self.context['request'].user
        request = self.context['request']

        if not User.objects.filter(id=self.context['view'].kwargs.get('id')
                                   ).exists():
            raise serializers.ValidationError(
                'Пользователя с таким id не существует')

        author = get_object_or_404(User,
                                   id=self.context['view'].kwargs.get('id'))

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
        author = get_object_or_404(User, id=self.context['view'].kwargs.get('id'))
        return Follow.objects.filter(user=self.context['request'].user,
                                     author=author).exists()


class FollowingGetSerializer(FollowSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes')
        read_only_fields = ('__all__',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if not recipes_limit:
            return AlterRecipeSerializer(recipes, many=True).data
        return AlterRecipeSerializer(recipes[:int(recipes_limit)],
                                     many=True).data
