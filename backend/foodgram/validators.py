from django.core.validators import RegexValidator
from .constants import NAME_REGEX

FIELD_VALIDATOR = RegexValidator(
    regex=NAME_REGEX,
    message="Это поле может содержать только буквы и пробелы.",
    code="invalid_name"
)
