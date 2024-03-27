from django.contrib import admin
from .models import Recipe, Tag, Ingredient, IngredientRecipe, User

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
