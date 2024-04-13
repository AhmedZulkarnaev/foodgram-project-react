from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.decorators import action
from .serializers import (
    RecipeCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    UserSerializer,
    ShortInfoRecipeSerializer,
    SubscriptionSerializer,
    UserCreateSerializer,
    SubscriptionListSerializer
)
from .filters import RecipeFilter, IngredientSearchFilter
from foodgram.models import (
    Recipe,
    Tag, Ingredient, User, Favorite, Cart, IngredientRecipe, Subscription)
from .paginations import PageLimitPagination
from api.permissions import IsAdminAuthorOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для пользователей.
    Позволяет выполнять операции CRUD для пользователей.
    Так же предоставляет методы для получения информации о текущем пользователе
    и изменения пароля.
    """

    queryset = User.objects.all()
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserCreateSerializer

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

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        """Позволяет текущему пользователю подписываться/отписываться от
        от автора контента, чей профиль он просматривает."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'subscriber': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionListSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscription, subscriber=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        """Возвращает авторов контента, на которых подписан
        текущий пользователь.."""
        authors = User.objects.filter(author__subscriber=request.user)
        paginator = PageLimitPagination
        result_pages = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = SubscriptionListSerializer(
            result_pages, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для рецептов.
    Позволяет выполнять операции CRUD для рецептов.
    Так же предоставляет методы для добавления/удаления рецепта в избранное.
    """

    queryset = Recipe.objects.all()
    permission_classes = [IsAdminAuthorOrReadOnly,]
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def add_method(self, model, user, name, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            return Response(
                {"errors": f"Нельзя повторно добавить рецепт в {name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortInfoRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_method(self, model, user, name, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": f"Нельзя повторно удалить рецепт из {name}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        url_name="favorite",
    )
    def get_favorite(self, request, pk):
        user = request.user
        name = "избранного"
        if request.method == "POST":
            return self.add_method(Favorite, user, name, pk)
        return self.delete_method(Favorite, user, name, pk)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def get_in_shopping_to_cart(self, request, pk):
        user = request.user
        name = "списка покупок"
        if request.method == "POST":
            return self.add_method(Cart, user, name, pk)
        return self.delete_method(Cart, user, name, pk)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_recipe_list(self, requset):
        recipe_in_cart = Cart.objects.filter(user=requset.user)
        recipe = [recipe_.recipe.id for recipe_ in recipe_in_cart]
        download_recipes = (
            IngredientRecipe.objects.filter(recipe__in=recipe)
            .values("ingredient")
            .annotate(amount=Sum("amount"))
        )
        download_list = [
            "Список покупок: "
        ]
        for recipe_ in download_recipes:
            ingredient = Ingredient.objects.get(pk=recipe_["ingredient"])
            amount = recipe_["amount"]
            download_list.append(
                f"{ingredient.name}: {amount}, "
                f"{ingredient.measurement_unit}"
            )
        file_content = "\n".join(download_list)
        response = HttpResponse(file_content, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; filename=recipe_list.txt"
        )
        return response


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
    filterset_class = IngredientSearchFilter
    search_fields = ("^name",)
    pagination_class = None
