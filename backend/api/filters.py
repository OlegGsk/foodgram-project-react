from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.NumberFilter(
        field_name='author__id',
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        # print(queryset.filter(is_in_shopping_cart=False))
        if value:
            return queryset.filter(is_favorited=True,)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        # print(value)
        if value:
            return queryset.filter(is_in_shopping_cart=True)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
