from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.response import Response
from recipes.models import Recipe


def create_delete_instance(request, model, serializer, id):
    if not Recipe.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data='Рецепт не найден')
    recipe = get_object_or_404(Recipe, id=id)
    serializer = serializer(data=request.data, context={'request': request,
                                                        'recipe': recipe})
    if request.method == 'POST':
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        serializer.is_valid(raise_exception=True)
        model.objects.filter(user=request.user,
                             recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)