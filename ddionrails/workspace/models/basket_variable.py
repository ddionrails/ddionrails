# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.workspace app: BasketVariable """

from django.core.exceptions import ValidationError
from django.db import models

from ddionrails.data.models import Variable

from .basket import Basket


class BasketVariable(models.Model):
    """
    Stores a single basket variable,
    related to :model:`workspace.Basket` and :model:`data.Variable`
    """

    #############
    # relations #
    #############
    basket = models.ForeignKey(
        Basket,
        related_name="baskets_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to workspace.Basket",
    )
    variable = models.ForeignKey(
        Variable,
        related_name="baskets_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Variable",
    )

    class Meta:
        """ Django's metadata options """

        unique_together = ("basket", "variable")

    def clean(self):
        """ Custom clean method for BasketVariable
            the basket's study and the variable's dataset's study have to be the same.
        """
        basket_study = self.basket.study
        variable_study = self.variable.dataset.study
        if not basket_study == variable_study:
            raise ValidationError(
                f'Basket study "{basket_study}" does not match variable study "{variable_study}"'
            )
        super(BasketVariable, self).clean()
