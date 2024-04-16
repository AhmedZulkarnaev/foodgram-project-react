from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import (MAX_LENGTH_EMAIL, MAX_LENGTH_NAME, MAX_LENGTH_SLUG,
                        MAX_LENGTH_USERNAME)
from .validators import validate_username


class User(AbstractUser):
    """
    Пользовательская модель пользователя, расширяющая AbstractUser Django.

    Атрибуты:
        username (str): Уникальное имя пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        email (str): Email адрес пользователя.
    """

    username = models.CharField(
        verbose_name="Логин",
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username
        ]
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_NAME,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LENGTH_NAME,
    )
    email = models.EmailField(
        verbose_name="Email пользователя",
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Tag(models.Model):
    """
    Модель представляющая тег для рецептов.

    Атрибуты:
        name (str): Название тега.
        color (str): Код цвета тега.
        slug (str): Slug для тега.
    """

    name = models.CharField(
        "Название", max_length=MAX_LENGTH_NAME, unique=True
    )
    color = models.CharField("Цветовой код", max_length=7)
    slug = models.SlugField("slug", max_length=MAX_LENGTH_SLUG, unique=True)

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Модель представляющая ингредиент.

    Атрибуты:
        name (str): Название ингредиента.
        measurement_unit (str): Единица измерения ингредиента.
    """

    name = models.CharField(max_length=MAX_LENGTH_NAME)
    measurement_unit = models.CharField(max_length=MAX_LENGTH_NAME)

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель представляющая рецепт.

    Атрибуты:
        author (User): Автор рецепта.
        name (str): Название рецепта.
        image (ImageField): Изображение рецепта.
        text (str): Описание рецепта.
        ingredients (ManyToManyField): Ингредиенты рецепта.
        tags (ManyToManyField): Теги рецепта.
        cooking_time (int): Время приготовления рецепта в минутах.
    """

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes"
    )
    name = models.CharField(max_length=MAX_LENGTH_NAME)
    image = models.ImageField(upload_to="recipe_images/")
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """
    Модель связи ингредиента и рецепта.

    Атрибуты:
        ingredient (Ingredient): Связанный ингредиент.
        recipe (Recipe): Связанный рецепт.
        amount (int): Количество ингредиента в рецепте.
    """

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        verbose_name = "ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"

    def __str__(self):
        return f"{self.ingredient} - {self.amount}"


class Favorite(models.Model):
    """
    Модель для избранных рецептов пользователей.

    Атрибуты:
        user (User): Пользователь, добавивший в избранное.
        recipe (Recipe): Рецепт, добавленный в избранное.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites_user"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites_recipe"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"{self.recipe} в избранном у пользователя {self.user}"


class Cart(models.Model):
    """
    Модель для корзины покупок пользователей.

    Атрибуты:
        user (User): Пользователь, добавивший в корзину.
        recipe (Recipe): Рецепт, добавленный в корзину.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart_user"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="cart_recipe"
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_list_recipe"
            )]

    def __str__(self):
        return (
            f"Рецепт {self.recipe} в списке покупок у пользователя {self.user}"
        )


class Subscription(models.Model):
    """
    Модель подписки.

    Атрибуты:
        user: Внешний ключ к модели User, представляющий подписчика.
        author: Внешний ключ к модели User, представляющий автора.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
