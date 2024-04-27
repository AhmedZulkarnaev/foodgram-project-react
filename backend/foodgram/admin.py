from django.contrib import admin

from .forms import IngredientRecipeFormSet
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     Subscription, Tag, User)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1
    formset = IngredientRecipeFormSet


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author_name', 'quantity_favorite')
    list_filter = ('tags__name',)
    search_fields = ('author_name', 'name')
    inlines = (IngredientRecipeInline,)

    def quantity_favorite(self, obj):
        return obj.favorites_recipe.count()

    def author_name(self, obj):
        return obj.author.username


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite)
admin.site.register(Subscription)
