from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet

router_v1 = DefaultRouter()

router_v1.register('tags', viewset=TagViewSet, basename='tags')
router_v1.register('ingredients', viewset=IngredientViewSet,
                   basename='ingredients')
router_v1.register('recipes', viewset=RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('users.urls'))]
