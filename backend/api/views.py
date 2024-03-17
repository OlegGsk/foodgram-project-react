
import csv

from api.filters import RecipeFilter
from api.permissions import IsAutehenticatedOrAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             ShoppingCartSerializer, TagSerializer,
                             FavoriteSerializer)
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from djoser.views import UserViewSet
from django.db.models import Exists, Subquery
from django.contrib.auth.decorators import login_required
from recipes.models import (Ingredient, Recipe, ShoppingCart, Tag,
                            Favorites)
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
    # queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend,]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [IsAutehenticatedOrAuthorOrReadOnly]
    
    def get_queryset(self):
        return Recipe.objects.all().annotate(
            is_favorited=Exists(
                Subquery(Favorites.objects.filter(
                    user=self.request.user,
                    recipe_id=self.kwargs.get('pk'))))
            ).annotate(
            is_in_shopping_cart=Exists(
                Subquery(ShoppingCart.objects.filter(
                    user=self.request.user,
                    recipe_id=self.kwargs.get('pk')
                ))))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    http_method_names = ['post', 'delete']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorites.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        recipe=self.get_recipe())

    def get_object(self):
        return get_object_or_404(Favorites, user=self.request.user,
                                 recipe=self.get_recipe())

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('id'))


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        recipe=self.get_recipe())

    def get_object(self):
        return get_object_or_404(ShoppingCart, user=self.request.user,
                                 recipe=self.get_recipe())

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs.get('id'))


class DownloadShoppingCart(APIView):
    def get(self, request):
        recipes = ShoppingCart.objects.filter(user_id=14).values(
            'recipe__name', 'recipe__ingredients__name', 'recipe__ingredients__measurement_unit').aaggregate(
                sum=Sum('recipe__ingredients__amount'))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.csv"'

        writer = csv.writer(response)
        writer.writerow(['Рецепт', 'Количество', 'Единицы измерения'])

        for recipe in recipes:
            writer.writerow([recipe['recipe__name'], recipe['sum'],
                             recipe['recipe__ingredients__measurement_unit']])

        return response