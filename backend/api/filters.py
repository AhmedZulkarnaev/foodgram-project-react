import django_filters
from foodgram.models import Recipe, Tag, Ingredient


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ['tags']


class IngredientFilter(django_filters.FilterSet):
    starts_with_name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith'
        )
    contains_name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
        )

    class Meta:
        model = Ingredient
        fields = ['starts_with_name', 'contains_name']
