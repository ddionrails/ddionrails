from django.core.exceptions import ValidationError


def validate_lowercase(value):
    if not value.islower():
        raise ValidationError(f"{value} is not lower case.")
