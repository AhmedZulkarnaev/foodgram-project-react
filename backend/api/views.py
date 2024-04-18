from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsAuthorOrReadOnly
from foodgram.models import (
    Cart, Favorite, Ingredient, IngredientRecipe,
    Recipe, Subscription, Tag, User
)
from .filters import RecipeFilter
from .serializers import (
    IngredientSerializer, RecipeCreateSerializer,
    ShortInfoRecipeSerializer, SubscriptionListSerializer,
    TagSerializer
)


class CustomUserViewSet(UserViewSet):
    """
    ViewSet для пользователей.

    Позволяет выполнять операции CRUD для пользователей.
    Так же предоставляет методы для получения информации о текущем пользователе
    и изменения пароля.
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        """Права доступа."""
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = self.request.user
        queryset = user.subscriber.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionListSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
        url_path="subscribe",
        url_name="subscribe",
    )
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if user == author:
            return Response(
                {"errors": "Нельзя подписаться или отписаться от себя!"},
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
                user=user, author=author
            ).exists():
                return Response(
                    {"errors": "Вы уже отписаны!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
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
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def add_method(self, model, user, name, pk):
        """Метод добавления/создания объекта."""
        try:
            recipe = get_object_or_404(Recipe, pk=pk)
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": f"Нельзя повторно добавить рецепт в {name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortInfoRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"errors": f"Ошибка при добавлении рецепта в {name}: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
        permission_classes=(permissions.IsAuthenticated,)
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
        permission_classes=(permissions.IsAuthenticated,)
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
        methods=("get",),
        permission_classes=(permissions.IsAuthenticated,),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        """Метод скачивания списка покупок."""
        shopping_cart = Cart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy = (
            IngredientRecipe.objects.filter(recipe__in=recipes)
            .values("ingredient")
            .annotate(amount=Sum("amount"))
        )
        list_recipe = [
            "Список покупок:",
        ]
        for item in buy:
            ingredient = Ingredient.objects.get(pk=item["ingredient"])
            amount = item["amount"]
            list_recipe.append(
                f"{ingredient.name}: {amount}, "
                f"{ingredient.measurement_unit}"
            )
        purchased_in_file = "\n".join(list_recipe)

        response = HttpResponse(purchased_in_file, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = "attachment; filename=shopping-list.txt"

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
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )
    pagination_class = None
