import base64
from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers
from foodgram.models import Recipe, Ingredient, Tag, IngredientRecipe, User


class UserSerializer(DjoserCreateSerializer):
    class Meta(DjoserCreateSerializer.Meta):
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name'
        )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для описания ингредиентов в рецепте."""

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
    """Сериализатор для добавления ингредиента"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a recipe."""

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
        author = self.context['request'].user
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
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
    """Serializer for listing a recipe."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(
        source='ingredientrecipe_set', many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
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
