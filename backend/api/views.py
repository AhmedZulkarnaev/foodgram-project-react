from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import (
    FavoriteSerializer,
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    UserSerializer,
    ShortInfoRecipeSerializer
)
from .filters import RecipeFilter, IngredientFilter
from foodgram.models import Recipe, Tag, Ingredient, User, Favorite
from rest_framework.pagination import LimitOffsetPagination


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для пользователей.
    Позволяет выполнять операции CRUD для пользователей.
    Так же предоставляет методы для получения информации о текущем пользователе
    и изменения пароля.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="me"
    )
    def get_current_user_info(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="set_password"
    )
    def set_password(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        if not user.check_password(current_password):
            return Response(
                {"error": "Incorrect current password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для рецептов.
    Позволяет выполнять операции CRUD для рецептов.
    Так же предоставляет методы для добавления/удаления рецепта в избранное.
    """

    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        url_name="favorite",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user.id
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={"user": user, "recipe": recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = ShortInfoRecipeSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=user, recipe=recipe
            ).first()
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "This recipe is not in favorites."},
                status=status.HTTP_400_BAD_REQUEST
            )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для тегов.
    Позволяет выполнять операцию чтения для тегов.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для ингредиентов.
    Позволяет выполнять операцию чтения для ингредиентов.
    Дополнительно предоставляет возможность фильтрации списка ингредиентов.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None
