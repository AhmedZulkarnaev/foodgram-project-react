from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     Subscription, Tag, User)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author_name')
    list_filter = ('tags__name',)
    search_fields = ('author_name', 'name')

    def author_name(self, obj):
        return obj.author.username


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Favorite)
admin.site.register(Subscription)
