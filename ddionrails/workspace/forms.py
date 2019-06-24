# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

""" ModelForms for ddionrails.workspace app """

from django import forms
from django.contrib.auth.forms import UserCreationForm as UCF
from django.contrib.auth.models import User

from .models import Basket


class UserCreationForm(UCF):
    class Meta:
        model = User
        fields = ("username", "email")


class BasketForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ("name", "label", "description", "study", "user")
