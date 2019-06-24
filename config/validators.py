# -*- coding: utf-8 -*-

""" Custom validators for ddionrails project """

from django.core.exceptions import ValidationError


def validate_lowercase(value):
    """ Raises a ValidationError if value is not lower case """
    if not value == value.lower():
        raise ValidationError(f"{value} is not lower case.")
