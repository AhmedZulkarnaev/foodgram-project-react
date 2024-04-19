from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q

from .constants import (MAX_LENGTH_EMAIL, MAX_LENGTH_NAME, MAX_LENGTH_SLUG,
                        MAX_LENGTH_USERNAME, MAX_LENGTH_COLOR)
from .validators import FIELD_VALIDATOR


class User(AbstractUser):
    """
    Пользовательская модель пользователя, расширяющая AbstractUser Django.

    Атрибуты:
        username (str): Уникальное имя пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        email (str): Email адрес пользователя.
    """
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    username = models.CharField(
        verbose_name="Логин",
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
        ]
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_LENGTH_NAME,
        validators=[FIELD_VALIDATOR]
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_LENGTH_NAME,
        validators=[FIELD_VALIDATOR]
    )
    email = models.EmailField(
        verbose_name="Email пользователя",
        max_length=MAX_LENGTH_EMAIL,
        unique=True
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
        "Название",
        max_length=MAX_LENGTH_NAME,
        unique=True,
        validators=[FIELD_VALIDATOR]
    )
    color = models.CharField(
        "Цветовой код",
        max_length=MAX_LENGTH_COLOR,
        validators=[
            RegexValidator(
                regex=r"^#[a-fA-F0-9]*$",
                message="Цветовой код должен быть в формате HEX.",
                code="invalid_color_code"
            )
        ]
    )
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

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        validators=[FIELD_VALIDATOR]
    )
    measurement_unit = models.CharField(max_length=MAX_LENGTH_NAME)

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

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
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

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

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='+'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

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
        User, on_delete=models.CASCADE, related_name="+"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites_recipe"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

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
        User, on_delete=models.CASCADE, related_name="+"
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
        related_name="subscriber",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_subscription"
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='different_user_and_author'
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
