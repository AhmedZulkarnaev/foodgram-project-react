from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    UserSerializer,
)
from .filters import RecipeFilter
from foodgram.models import Recipe, Tag, Ingredient, User
from .permissions import IsAdminOrReadOnly
from rest_framework.pagination import LimitOffsetPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    page_size = 6

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    page_size = 6


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
