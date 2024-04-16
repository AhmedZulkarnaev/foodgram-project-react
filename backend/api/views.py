from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import (
    AnonimOrAuthenticatedReadOnly, IsAdminAuthorOrReadOnly
    )
from foodgram.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Subscription,
    Tag,
    User,
)

from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    ShortInfoRecipeSerializer,
    SubscriptionListSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для пользователей.

    Позволяет выполнять операции CRUD для пользователей.
    Так же предоставляет методы для получения информации о текущем пользователе
    и изменения пароля.
    """

    queryset = User.objects.all()
    permission_classes = [AnonimOrAuthenticatedReadOnly]

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от HTTP-запроса."""
        if self.request.method == "GET":
            return UserSerializer
        return UserCreateSerializer

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="me",
    )
    def get_current_user_info(self, request):
        """Возвращает информацию о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        url_path="set_password",
    )
    def set_password(self, request):
        """Устанавливает новый пароль текущему пользователю."""
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        if not user.check_password(current_password):
            return Response(
                {"error": "Incorrect current password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("GET",),
        permission_classes=[permissions.IsAuthenticated],
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = self.request.user
        subscribe = user.follower.all()
        pages = self.paginate_queryset(subscribe)
        serializer = SubscriptionListSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        permission_classes=[permissions.IsAuthenticated],
        url_path="subscribe",
        url_name="subscribe",
    )
    def subscribe(self, request, pk):
        """Подписка на автора."""
        user = self.request.user
        author = get_object_or_404(User, pk=pk)
        if author == user:
            return Response(
                {"errors": "Подписка уже оформлена!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if self.request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "Подписка уже оформлена!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = Subscription.objects.create(author=author, user=user)
            serializer = SubscriptionListSerializer(
                queryset, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not Subscription.objects.filter(
                    user=user, author=author).exists():
                return Response(
                    {"errors": "Вы уже отписаны!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription = get_object_or_404(
                Subscription, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для рецептов.

    Позволяет выполнять операции CRUD для рецептов.
    Так же предоставляет методы для добавления/удаления рецепта в избранное.
    """

    queryset = Recipe.objects.all()
    permission_classes = [
        IsAdminAuthorOrReadOnly,
    ]
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def add_method(self, model, user, name, pk):
        """Метод добавления/создания объекта."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"errors": f"Нельзя повторно добавить рецепт в {name}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortInfoRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_method(self, model, user, name, pk):
        """Метод удаления объекта."""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if model.objects.filter(user=user, recipe=recipe).exists():
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
        """Метод добавления/удаления объекта из избранное."""
        user = request.user
        name = "избранное"
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
        """Метод добавления/удаления объекта из корзины."""
        user = request.user
        name = "список покупок"
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
        """Метод скачивания ингредиентов из списка покупок."""
        recipe_in_cart = Cart.objects.filter(user=requset.user)
        recipe = [recipe_.recipe.id for recipe_ in recipe_in_cart]
        download_recipes = (
            IngredientRecipe.objects.filter(recipe__in=recipe)
            .values("ingredient")
            .annotate(amount=Sum("amount"))
        )
        download_list = ["Список покупок: "]
        for recipe_ in download_recipes:
            ingredient = Ingredient.objects.get(pk=recipe_["ingredient"])
            amount = recipe_["amount"]
            download_list.append(
                f"{ingredient.name}: {amount}, ",
                f"{ingredient.measurement_unit}"
            )
        file_content = "\n".join(download_list)
        response = HttpResponse(file_content, content_type="text/plain")
        response[
            "Content-Disposition"] = "attachment; filename=recipe_list.txt"
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
