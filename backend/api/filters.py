import django_filters
from foodgram.models import Recipe, Tag, Ingredient


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтр для рецептов.
    Позволяет фильтровать рецепты по тегам, автору и наличию в избранном.
    """

    is_favorited = django_filters.NumberFilter(
        method='get_favorite_recipes'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    author = django_filters.AllValuesMultipleFilter(
        field_name='author__username'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited')

    def get_favorite_recipes(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по избранному.
        """

        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorites_recipe__user=self.request.user
            )
        return queryset


class IngredientFilter(django_filters.FilterSet):
    """
    Фильтр для ингредиентов.
    Позволяет фильтровать ингредиенты по началу и частичному совпадению имени.
    """

    starts_with_name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
        )
    contains_name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
        )

    class Meta:
        model = Ingredient
        fields = ['starts_with_name', 'contains_name']
