from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from foodgram.models import User, Recipe, Tag, Ingredient
from rest_framework import serializers


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


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'ingredients', 'image',  'description', 'tag'
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TagSerializers(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class IngredientSerializers(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'quantity', 'unit')
