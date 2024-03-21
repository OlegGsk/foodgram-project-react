from django.db import transaction
from rest_framework import serializers

from core.utils import Base64ImageField
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name',
                                 required=False)
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
        required=False)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('__all__',)


class IngredientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientSerializer(source='recipe_ingredients', many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')
        # read_only_fields = ('author', 'id', 'is_favorited',
        #                     'is_in_shopping_cart')

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег')
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться!!')
        return value

    def validate_ingredients(self, value):
        ingredients_id_list = []

        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент')
        for ingredient in value:
            id = ingredient.get('ingredients').get('id')
            amount = ingredient.get('amount')
            ingredients_id_list.append(id)
            if not Ingredient.objects.filter(id=id).exists():
                raise serializers.ValidationError(
                    f'Ингредиента с id {id} нет в базе данных!!')

            if amount <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля')

        if len(ingredients_id_list) != len(set(ingredients_id_list)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!!')
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for ingredient in ingredients:
            id = ingredient.get('ingredients').get('id')
            amount = ingredient.get('amount')
            current_ingredient = Ingredient.objects.get(
                id=id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredients=current_ingredient,
                amount=amount)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        instance.is_favorited = False
        instance.is_in_shopping_cart = False
        return RecipeGetSerializer(instance, context={'request': request}).data

    @transaction.atomic
    def update(self, instance, validated_data):
        if ('ingredients' not in self.initial_data
                or 'tags' not in self.initial_data):
            raise serializers.ValidationError(
                'При обновлении рецепта необходимо добавить ингредиент!'
                ' или тег!!'
            )
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        if 'recipe_ingredients' in validated_data:
            ingredients = validated_data.pop('recipe_ingredients')
            RecipeIngredient.objects.filter(recipe=instance).delete()
            for ingredient in ingredients:
                id = ingredient.get('ingredients').get('id')
                amount = ingredient.get('amount')
                ingredient = Ingredient.objects.get(
                    id=id)
                RecipeIngredient.objects.create(
                    recipe=instance, ingredients=ingredient,
                    amount=amount)

        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            RecipeTag.objects.filter(recipe=instance).delete()
            for tag in tags:
                RecipeTag.objects.create(recipe=instance, tag=tag)

        instance.save()
        return instance


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(source='recipe_ingredients',
                                       many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('__all__',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    message_post = 'Рецепт уже добавлен в список покупок'
    message_delete = 'Рецепта нет в списке покупок'

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST' and self.is_located():
            raise serializers.ValidationError(
                self.message_post)
        if request.method == 'DELETE' and not self.is_located():
            raise serializers.ValidationError(
                self.message_delete)
        return data

    def is_located(self):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        return self.Meta.model.objects.filter(user_id=user.id, recipe=recipe
                                              ).exists()


class FavoriteSerializer(ShoppingCartSerializer):
    message_post = 'Рецепт уже добавлен в избранное'
    message_delete = 'Рецепта нет в избранном'

    class Meta:
        model = Favorites
        fields = ('id', 'name', 'image', 'cooking_time')
