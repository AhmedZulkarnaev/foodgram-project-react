import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from foodgram.models import (
    Favorite,
    Recipe, Ingredient, Tag, IngredientRecipe, User, Cart, Subscription
)


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользовательской модели.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользовательской модели.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        user_id = self.context.get("request").user.id
        return Subscription.objects.filter(
            author=obj.id, user=user_id
        ).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели подписок.
    """

    class Meta:
        model = Subscription
        fields = "__all__"


class SubscriptionListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели подписок,
    предназначенный для отображения информации о подписках.
    """

    id = serializers.ReadOnlyField(source="author.id")
    email = serializers.ReadOnlyField(source="author.email")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source="author.recipes.count")
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        user_id = self.context.get("request").user.id
        return Subscription.objects.filter(
            author=obj.id, user=user_id
        ).exists()

    def get_recipes(self, obj):
        author_recipes = obj.author.recipes.all()
        return ShortInfoRecipeSerializer(author_recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.id).count()


class Base64ImageField(serializers.ImageField):
    """
    Декодирование изображения из base64.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для описания ингредиентов в рецепте.
    """

    name = serializers.CharField(source="ingredient.name", read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient.id", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class NewIngredientAddSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиента.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецепта.
    """

    author = UserSerializer(read_only=True)
    ingredients = NewIngredientAddSerializer(
        many=True, write_only=True, required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        if "tags" not in data or len(data["tags"]) < 1:
            raise serializers.ValidationError("Должен быть хотя бы один тег")

        if "ingredients" not in data or len(data["ingredients"]) < 1:
            raise serializers.ValidationError(
                "Должен быть хотя бы один ингредиент"
            )

        if data.get("cooking_time", 0) < 1:
            raise serializers.ValidationError(
                "Время готовки должно быть не менее 1"
            )

        tags = data.get("tags", [])
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError("Теги не должны повторяться")

        ingredients = data.get("ingredients", [])
        ingredient_names = [item["ingredient"] for item in ingredients]
        if len(set(ingredient_names)) != len(ingredient_names):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться"
            )

        if any(item.get("amount", 0) < 1 for item in ingredients):
            raise serializers.ValidationError(
                "Количество ингредиента должно быть не менее 1"
            )

        return data

    def get_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient.get("ingredient"),
                amount=ingredient.get("amount"),
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        author = self.context["request"].user
        tags_data = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.get_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return RecipeListSerializer(instance, context=context).data


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка рецептов.
    """

    author = UserSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(
        source="ingredientrecipe_set", many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart"
        )

    def check_validate(self, model, object):
        user_id = self.context.get("request").user.id
        return model.objects.filter(user=user_id, recipe=object.id).exists()

    def get_is_favorited(self, obj):
        return self.check_validate(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self.check_validate(Cart, obj)


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка покупок.
    """
    class Meta:
        model = Cart
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавили этот рецепт в список покупок"
            )
        ]

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return ShortInfoRecipeSerializer(instance.recipe, context=context).data


class ShortInfoRecipeSerializer(serializers.ModelSerializer):
    """
    Краткий сериализатор для рецепта.
    """
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранных рецептов.
    """

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавили этот рецепт в избранное"
            )
        ]

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return ShortInfoRecipeSerializer(instance.recipe, context=context).data
