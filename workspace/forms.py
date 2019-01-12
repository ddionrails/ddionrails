from django import forms
from django.contrib.auth.forms import UserCreationForm as UCF
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from data.models import Variable
from studies.models import Study

from .models import Basket, BasketVariable


class UserCreationForm(UCF):
    class Meta:

        model = User
        fields = ["username", "email"]


class UserForm(forms.ModelForm):
    class Meta:

        model = User
        fields = ["username", "email", "password"]


class BasketForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ["name", "label", "description", "security_token", "study", "user"]


class BasketCSVForm(BasketForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data["name"] != self.data["name"].lower():
            self.data["cs_name"] = self.data["name"]
            self.data["name"] = self.data["name"].lower()
        if "study" not in self.data.keys():
            self.data["study"] = Study.objects.get(
                name=self.data["study_name"].lower()
            ).pk
        if "user" not in self.data.keys():
            self.data["user"] = User.objects.get(username=self.data["username"]).pk


class BasketVariableForm(forms.ModelForm):
    class Meta:
        model = BasketVariable
        fields = ["basket", "variable"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "basket" not in self.data.keys():
            self.data["basket"] = Basket.get_or_create(
                self.data["basket_name"], self.data["username"]
            ).pk
        if "variable" not in self.data.keys():
            try:
                self.data["variable"] = Variable.get(
                    dict(
                        study_name=self.data.get("study_name"),
                        dataset_name=self.data.get("dataset_name"),
                        name=self.data.get("variable_name"),
                    )
                ).pk
            except ObjectDoesNotExist:
                self.data["variable"] = None
