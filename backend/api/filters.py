from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet, filters

from foodgram.models import Recipe, Tag, User


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов.
    Позволяет фильтровать рецепты по тегам, автору и наличию в избранном.
    """
    is_favorited = filters.BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="filter_is_in_shopping_cart"
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    def filter_is_favorited(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по избранному.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по корзине.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart_recipe__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")
