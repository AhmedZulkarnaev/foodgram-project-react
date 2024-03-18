from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from .validators import validate_username
from .constants import (
    MAX_LENGTH_USERNAME, MAX_LENGTH_NAME, MAX_LENGTH_EMAIL
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_NAME,
    )
    email = models.EmailField(
        verbose_name='Email пользователя',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
