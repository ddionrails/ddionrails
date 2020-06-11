# -*- coding: utf-8 -*-

""" Model definitions for ddionrails.workspace app: BasketVariable """

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from ddionrails.data.models import Variable

from .basket import Basket


class BasketVariable(models.Model):
    """Links a Basket to its variables.

    related to :model:`workspace.Basket` and :model:`data.Variable`

    on_delete, of the variable ForeignKey is set to DO_NOTHING.
    This is done to keep this data, if the variable data is removed.
    The use case for this is when all data from a study is to be removed to get
    a clean import.
    BasketVariables are user generated and cannot be imported like study data.
    This means we do not want to delete them during the clean import process.

    It is possible, that the name of a variable changes, which will lead to a
    different id. This will leave BasketVariables, that do not point to an existing
    variable. remove_dangling_basket_variables can be used to clean them up.
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
        on_delete=models.DO_NOTHING,
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
    def remove_dangling_basket_variables(study_name: str = None):
        """Remove all BasketVariables that are not linked with an existing Variable.

        The variable ForeignKey is set to not Cascade on delete of the linked variable.
        This makes it possible to freshly ingest study data without removing user data
        in the form of variables in baskets.
        It is possible that variables may change names.
        This means it is also possible that ForeignKeys no longer point to an existing
        variable after an update.
        These BasketVariables should be removed after an update.

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
