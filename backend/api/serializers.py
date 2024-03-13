from pkg_resources import require
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from recipes.models import (Tag, Ingredient, Recipe,
                            RecipeTag, RecipeIngredient,
                            ShoppingCart)
from api.extra_fields_serializers import Base64ImageField
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(required=False,
                                      source='recipe_ingredients__amount')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id',)

    def to_representation(self, instance):
        amount = instance.recipe_ingredients.values('amount').last()
        print(amount)
        return {
            'id': instance.id,
            'name': instance.name,
            'measurement_unit': instance.measurement_unit,
            'amount': amount.get('amount')
        }


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'id', 'is_favorited',
                            'is_in_shopping_cart')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            amount = ingredient.get('recipe_ingredients__amount', 0)
            print(ingredient.get('name'))
            current_ingredient = Ingredient.objects.get(name=ingredient.get('name'))
            RecipeIngredient.objects.create(
                recipe=recipe, ingredients=current_ingredient,
                amount=amount)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        RecipeTag.objects.filter(recipe=instance).delete()
        for tag in tags:
            RecipeTag.objects.create(recipe=instance, tag=tag)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(name=ingredient.get('name'))
            RecipeIngredient.objects.create(
                recipe=instance, ingredients=current_ingredient,
                amount=ingredient.get('recipes_ingredient__amount'))
        return instance

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context.get('request').user
        recipe = get_object_or_404(Recipe, pk=self.context.get('view').kwargs.get('id'))
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок')
        return data
