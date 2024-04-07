from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Проверка на допустимость имени пользователя.
    Проверяет, что имя пользователя не равно 'me'.
    """

    if value == 'me':
        raise ValidationError("Username 'me' is not allowed.")
