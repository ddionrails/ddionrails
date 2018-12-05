from django.core.exceptions import ValidationError


def validate_lowercase(value):
    if value != value.lower():
        raise ValidationError("%s is not lower case." % value)
