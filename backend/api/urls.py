from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecipeModelViewSet, TagViewSet, IngredientViewSet
)

router_v1 = DefaultRouter()
router_v1.register(r'recipes/', RecipeModelViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('api/', include(router_v1.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
