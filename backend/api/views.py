
import csv
from logging import Filter

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAutehenticatedOrAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientGetSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer)
from django.contrib.auth import get_user_model
from django.db.models import Exists, Subquery, Value, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.utils import create_delete_instance


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGetSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
    lookup_url_kwarg = 'id'


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [IsAutehenticatedOrAuthorOrReadOnly]
    lookup_url_kwarg = 'id'

    def get_queryset(self):

        user = self.request.user
        if self.action == 'list' or user.is_anonymous:
            return Recipe.objects.annotate(
                is_favorited=Exists(
                    Subquery(Favorites.objects.filter(
                        user_id=OuterRef('author_id'),
                        recipe_id=OuterRef('pk')))),
                is_in_shopping_cart=Exists(
                    Subquery(ShoppingCart.objects.filter(
                        user=OuterRef('author_id'),
                        recipe_id=OuterRef('pk')
                    )))).select_related('author'
                                        ).prefetch_related('tags',
                                                           'ingredients')

        return Recipe.objects.all().annotate(
            is_favorited=Exists(
                Subquery(Favorites.objects.filter(
                    user=self.request.user,
                    recipe_id=self.kwargs.get('id'))))
            ).annotate(
            is_in_shopping_cart=Exists(
                Subquery(ShoppingCart.objects.filter(
                    user=self.request.user,
                    recipe_id=self.kwargs.get('id')
                )))).select_related('author').prefetch_related('tags',
                                                             'ingredients')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, id):
        return create_delete_instance(request, Favorites,
                                      FavoriteSerializer, id)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, id):
        return create_delete_instance(request, ShoppingCart,
                                      ShoppingCartSerializer, id)


# class DownloadShoppingCart(APIView):
#     def get(self, request):
#         recipes = ShoppingCart.objects.filter(user_id=14).values(
#             'recipe__name', 'recipe__ingredients__name', 'recipe__ingredients__measurement_unit').aaggregate(
#                 sum=Sum('recipe__ingredients__amount'))

#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="shopping_list.csv"'

#         writer = csv.writer(response)
#         writer.writerow(['Рецепт', 'Количество', 'Единицы измерения'])

#         for recipe in recipes:
#             writer.writerow([recipe['recipe__name'], recipe['sum'],
#                              recipe['recipe__ingredients__measurement_unit']])

#         return response