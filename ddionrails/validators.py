from django.core.exceptions import ValidationError


def validate_lowercase(value):
    if not value == value.lower():
        raise ValidationError(f"{value} is not lower case.")
