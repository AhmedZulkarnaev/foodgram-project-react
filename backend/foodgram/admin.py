from django.contrib import admin
from .models import User, Recipe, Tag, Ingredient, RecipeIngredient

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
