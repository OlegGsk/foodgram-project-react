
from api.filters import RecipeFilter
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             TagSerializer, ShoppingCartSerializer)
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag, ShoppingCart
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from api.permissions import IsAuthorOrReadOnly

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
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend,]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('id'))
        serializer.save(user=self.request.user,
                        recipe=recipe)

    def get_object(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('id'))
        return get_object_or_404(ShoppingCart, user=self.request.user, recipe=recipe)


def download_shopping_cart(request):
    queryset = ShoppingCart.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(['Рецепт', 'Количество'])
    for recipe in queryset:
        writer.writerow([recipe.recipe.name, recipe.recipe.cooking_time])
    return response