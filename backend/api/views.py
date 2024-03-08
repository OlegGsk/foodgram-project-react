
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from recipes.models import Recipe, Tag, Ingredient
from api.serializers import TagSerializer

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']