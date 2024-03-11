from django.db import router
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import (TagViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartViewSet)


router = DefaultRouter()

router.register('tags', viewset=TagViewSet, basename='tags')
router.register('ingredients', viewset=IngredientViewSet,
                basename='ingredients')
router.register('recipes', viewset=RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:id>/shopping_cart/', ShoppingCartViewSet.as_view(
        {'post': 'create', 'delete': 'destroy'}
    )),
    path('', include('users.urls'))
    ]
