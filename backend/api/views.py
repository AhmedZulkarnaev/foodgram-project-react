from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import (
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    UserSerializer,
)
from .filters import RecipeFilter, IngredientFilter
from foodgram.models import Recipe, Tag, Ingredient, User
from rest_framework.pagination import LimitOffsetPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def get_current_user_info(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name_starts_with = self.request.query_params.get('name', None)
        if name_starts_with:
            queryset = queryset.filter(name__startswith=name_starts_with)
        return queryset
