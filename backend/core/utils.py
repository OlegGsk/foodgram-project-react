import base64
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag


def create_delete_instance(request, model, serializer, id):
    """Создание или удаление рецепта."""
    is_located_recipe = Recipe.objects.filter(id=id).exists()

    if request.method == 'POST':
        if not is_located_recipe:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data='Рецепт не найден')
        serializer = serializer(data=request.data,
                                context={'request': request,
                                         'recipe': get_recipe(id)})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=get_recipe(id))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        if not is_located_recipe:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data='Рецепт не найден')
        serializer = serializer(data=request.data,
                                context={'request': request,
                                         'recipe': get_recipe(id)})
        serializer.is_valid(raise_exception=True)
        model.objects.filter(user=request.user,
                             recipe=get_recipe(id)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_recipe(id):
    return get_object_or_404(Recipe, id=id)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def create_update_ingredients(ingredients, instance):
    """Создание или обновление ингредиентов рецепта."""
    for ingredient in ingredients:
        id = ingredient.get('ingredients').get('id')
        amount = ingredient.get('amount')
        ingredient = Ingredient.objects.get(id=id)
        RecipeIngredient.objects.create(recipe=instance,
                                        ingredients=ingredient,
                                        amount=amount)


def create_update_tags(tags, instance):
    """Создание или обновление тегов рецепта."""
    for tag in tags:
        RecipeTag.objects.create(recipe=instance, tag=tag)


def create_shopping_list(request):
    """Создание списка покупок."""
    ingredients = RecipeIngredient.objects.filter(
        recipe__shoppingcart__user=request.user).values(
        'ingredients__name',
        'ingredients__measurement_unit').annotate(
            total_amount=Sum('amount'))

    shop_list = ['Список покупок:\n']
    shop_list += ['наименование' + 23 * ' ' + 'количество'
                  '        единицы измерения\n']
    for ingredient in ingredients:
        len_1 = ' ' * (35 - len(ingredient['ingredients__name']))
        len_2 = (53 - (len(len_1) + len(ingredient["ingredients__name"])
                 + len(str(ingredient['total_amount'])))) * ' '
        shop_list.append(
            f'{ingredient["ingredients__name"]}'
            f'{len_1}{ingredient["total_amount"]}'
            f'{len_2}{ingredient["ingredients__measurement_unit"]}\n')
    return shop_list
