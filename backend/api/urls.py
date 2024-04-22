from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

from .views import (
    SubscriptionsViewSet, IngredientViewSet, RecipeViewSet, TagViewSet
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("subscriptions", SubscriptionsViewSet,
                basename="subscriptions")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/subscriptions/", SubscriptionsViewSet.as_view(
        {"get": "subscriptions"}), name="subscriptions"),
    path(
        "users/<int:pk>/subscribe/",
        SubscriptionsViewSet.as_view(
            {"post": "subscribe", "delete": "unsubscribe"}
        ), name="subscribe"),
    path("", include(router.urls)),
]
