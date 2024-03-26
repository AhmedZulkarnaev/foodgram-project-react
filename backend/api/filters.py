from django_filters import rest_framework as filters
from foodgram.models import Recipe, Tag


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=True,
    )

    class Meta:
        model = Recipe
        fields = ['tags']

    def filter_queryset(self, queryset):
        if len(self.request.GET.getlist('tags')) == Tag.objects.count():
            return queryset
        return queryset.filter(
            tags__slug__in=self.request.GET.getlist('tags')
        ).distinct()
