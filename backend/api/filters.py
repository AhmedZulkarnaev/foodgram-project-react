import django_filters

from foodgram.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтр для рецептов.
    Позволяет фильтровать рецепты по тегам, автору и наличию в избранном.
    """

    is_favorited = django_filters.NumberFilter(
        method="get_favorite_recipes"
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method="get_in_shopping_cart_recipes"
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug"
    )
    author = django_filters.NumberFilter(
        field_name="author__id", lookup_expr="exact"
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author", "is_favorited", "is_in_shopping_cart")

    def get_favorite_recipes(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по избранному.
        """

        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorites_recipe__user=self.request.user
            )
        return queryset

    def get_in_shopping_cart_recipes(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по корзине.
        """

        if value and self.request.user.is_authenticated:
            return queryset.filter(
                cart_recipe__user=self.request.user
            )
        return queryset


class IngredientSearchFilter(django_filters.FilterSet):
    """
    Фильтр поиска по названию ингредиента.
    """

    name = django_filters.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name", )
