from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Follow

User = get_user_model()


class AlterRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в подписках."""
    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ("__all__",)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для получения информации о пользователе."""
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


class FollowGetSerializer(CustomUserSerializer):
    """Сериализатор для получения информации о подписках."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes_count', 'is_subscribed', 'recipes')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name',
                            'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        user = self.context['request'].user
        request = self.context.get('request')
        if user.is_anonymous:
            return
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if not recipes_limit:
            return AlterRecipeSerializer(recipes, many=True).data
        return AlterRecipeSerializer(recipes[:int(recipes_limit)],
                                     many=True).data


class FollowPostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и удаления подписок."""
    class Meta:
        model = Follow
        fields = '__all__'
        read_only_fields = ('user', 'author')

    def to_representation(self, instance):
        return FollowGetSerializer(instance.author, context=self.context).data
