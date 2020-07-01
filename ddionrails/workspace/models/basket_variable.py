# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.workspace app: BasketVariable """

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from ddionrails.data.models import Variable

from .basket import Basket


class BasketVariable(models.Model):
    """Links a Basket to its variables.

    related to :model:`workspace.Basket` and :model:`data.Variable`
    """

    #############
    # relations #
    #############
    basket: models.ForeignKey = models.ForeignKey(
        Basket,
        related_name="baskets_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to workspace.Basket",
    )
    variable: models.ForeignKey = models.ForeignKey(
        Variable,
        related_name="baskets_variables",
        on_delete=models.CASCADE,
        help_text="Foreign key to data.Variable",
        db_constraint=False,
    )

    class Meta:
        """ Django's metadata options """

        unique_together = ("basket", "variable")

    def clean(self):
        """ Custom clean method for BasketVariable
            the basket's study and the variable's dataset's study have to be the same.
        """
        basket_study = self.basket.study  # pylint: disable=E1101
        variable_study = self.variable.dataset.study  # pylint: disable=E1101
        if not basket_study == variable_study:
            raise ValidationError(
                (
                    f'Basket study "{basket_study}" '
                    f'does not match variable study "{variable_study}"'
                )
            )
        super(BasketVariable, self).clean()

    def variable_key_exists(self) -> bool:
        """Check if the Variable ForeignKey still points to an existing object.

        Returns:
            True if ForeignKey still points to a Variable inside the database,
            otherwise it will return False.
        """
        try:
            Variable.objects.get(id=self.variable_id)
        except ObjectDoesNotExist:
            return False
        return True

    @staticmethod
    def clean_basket_variables(study_name: str = None):
        """Remove all BasketVariables that are not linked with an existing Variable.

        Basket restoration during a clean update might ingest outdated relations.

        Args:
            study_name: Limits clean up to variables linked to the study with the
                        specified name.
        """
        _filter = dict()
        if study_name:
            _filter["basket__study__name"] = study_name
        for basket_variable in BasketVariable.objects.filter(**_filter):
            if not basket_variable.variable_key_exists():
                basket_variable.delete()
