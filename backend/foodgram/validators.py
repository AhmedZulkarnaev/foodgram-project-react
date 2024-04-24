from django.core.validators import RegexValidator
from .constants import NAME_REGEX, COLOR_REGEX

FIELD_VALIDATOR = RegexValidator(
    regex=NAME_REGEX,
    message="Это поле может содержать только буквы и пробелы.",
    code="invalid_name"
)


def validate_hex_color(value):
    hex_color_validator = RegexValidator(
        regex=COLOR_REGEX,
        message="Цветовой код должен быть в формате HEX.",
        code="invalid_color_code"
    )
    hex_color_validator(value)
