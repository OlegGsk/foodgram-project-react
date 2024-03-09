
from api.filters import RecipeFilter
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeGetSerializer, RecipePostSerializer)
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import LimitOffsetPagination

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePostSerializer
    pagination_class = LimitOffsetPagination
    filter_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
