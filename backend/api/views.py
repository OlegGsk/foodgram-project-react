from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Subquery, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action


from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAutehenticatedOrAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientGetSerializer,
                             RecipeGetSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             TagSerializer)
from core.utils import create_delete_instance

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGetSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
    lookup_url_kwarg = 'id'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'delete', 'patch']
    permission_classes = [IsAutehenticatedOrAuthorOrReadOnly]
    lookup_url_kwarg = 'id'

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSerializer

    def get_queryset(self):

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

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            'ingredients__name',
            'ingredients__measurement_unit').annotate(amount=Sum('amount'))
        shop_list = ['Список покупок:\n']
        shop_list += ['наименование - количество - единицы измерения\n']
        for ingredient in ingredients:
            shop_list.append(
                f'{ingredient["ingredients__name"]}'
                f'          {ingredient["amount"]} '
                f'           {ingredient["ingredients__measurement_unit"]}\n'
            )

        response = HttpResponse(shop_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
