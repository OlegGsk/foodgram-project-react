from api.extra_fields_serializers import Base64ImageField
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
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
        amount = RecipeIngredient.objects.get(ingredients=instance,
                                              recipe_id=self.context.get(
                                                     'recipe_id')).amount
        return {
            'id': instance.id,
            'name': instance.name,
            'measurement_unit': instance.measurement_unit,
            'amount': amount
        }


class IngredientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags','image', 'name', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'id', 'is_favorited',
                            'is_in_shopping_cart')

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один тег')
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться!!')
        return value

    def validate_ingredients(self, value):
        ingredient_list = []
        if not value:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент')
        for ingredient in value:
            ingredient_list.append(ingredient.get('name'))
            if not Ingredient.objects.filter(name=ingredient.get('name')
                                             ).exists():
                raise serializers.ValidationError(f'{ingredient.get("name")}'
                                                  ' такого ингредиента нет')

            if ingredient.get('recipe_ingredients__amount') <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля')

        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!!')
        return value

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля')
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            amount = ingredient.get('recipe_ingredients__amount', 0)
            current_ingredient = Ingredient.objects.get(
                name=ingredient.get('name'), measurement_unit=ingredient.get(
                    'measurement_unit'
                ))
            RecipeIngredient.objects.create(
                recipe=recipe, ingredients=current_ingredient,
                amount=amount)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(instance, context={'request': request,
                                                      'recipe_id': instance.id}).data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        RecipeTag.objects.filter(recipe=instance).delete()
        for tag in tags:
            RecipeTag.objects.create(recipe=instance, tag=tag)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                name=ingredient.get('name'))
            RecipeIngredient.objects.create(
                recipe=instance, ingredients=current_ingredient,
                amount=ingredient.get('recipes_ingredient__amount', 0))
        return instance


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
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

    def get_ingredients(self, obj):
        return IngredientSerializer(obj.ingredients, many=True,
                                    context={'recipe_id': obj.id}).data


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
