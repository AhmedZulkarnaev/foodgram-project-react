import base64
from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from django.core.files.base import ContentFile
from rest_framework import serializers
import uuid
from foodgram.models import Recipe, Ingredient, Tag, IngredientRecipe, User


class UserCreateSerializer(DjoserCreateSerializer):
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
            file_name = str(uuid.uuid4()) + '.' + ext
            data = ContentFile(base64.b64decode(imgstr), name=file_name)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ['ingredient', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time'
        ]

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(recipe=recipe, **ingredient_data)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        ingredients_data = validated_data.get('ingredients')
        tags_data = validated_data.get('tags')

        IngredientRecipe.objects.filter(recipe=instance).delete()

        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(recipe=instance, **ingredient_data)
        instance.tags.set(tags_data)
        instance.save()
        return instance
