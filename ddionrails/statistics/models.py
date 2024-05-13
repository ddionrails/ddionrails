"""Models for the statistics-server App."""

from typing import Iterable, Optional

from django.db import models

from ddionrails.base.models import Singleton
from ddionrails.data.models.variable import Variable
from ddionrails.imports.helpers import hash_with_namespace_uuid

# Create your models here.


class GroupMetadata(Singleton):

    metadata = models.JSONField()


class IndependentVariable(models.Model):
    """Information about valuelabels for independent variables (dimensions)."""

    # Keys
    id = models.UUIDField(primary_key=True)
    variable = models.ForeignKey(to=Variable, null=False, on_delete=models.CASCADE)

    values = models.JSONField(default=list)
    labels = models.JSONField()

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if not self.id:
            self.id = hash_with_namespace_uuid(  # pylint: disable = invalid-name
                self.variable.id, f"{self.labels}"
            )

        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class StatisticsMetadata(models.Model):
    """Store data to be served by the REST API."""

    variable = models.ForeignKey(
        to=Variable,
        null=False,
        on_delete=models.CASCADE,
        related_name="statistics_metadata",
    )
    metadata = models.JSONField()


class VariableStatistic(models.Model):
    """Stores CSV statistics Data for a data.Variable."""

    class PlotType(models.TextChoices):
        """Define possible plot types."""

        CATEGORICAL = "categorical", "Categorical"
        NUMERICAL = "numerical", "Numerical"
        ORDINAL = "ordinal", "Ordinal"

    # Keys
    id = models.UUIDField(primary_key=True)
    variable = models.ForeignKey(
        to=Variable, null=False, on_delete=models.CASCADE, related_name="statistics_data"
    )

    # Attributes
    plot_type = models.TextField(null=False, choices=PlotType.choices)
    statistics = models.FileField(null=False, blank=False, upload_to="statistic_files/")
    independent_variables = models.ManyToManyField(
        null=True, blank=True, to=IndependentVariable
    )
    independent_variable_names = models.JSONField(default=[])
    start_year = models.IntegerField(null=False, blank=False)
    end_year = models.IntegerField(null=False, blank=False)

    def set_independent_variable_names(self, names: list[str]) -> None:
        """Save the names of related indep. var. in a helper field."""
        self.independent_variable_names = sorted(names)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if not self.id:
            self.id = hash_with_namespace_uuid(  # pylint: disable = invalid-name
                self.variable.id, f"{self.plot_type}{self.independent_variable_names}"
            )
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
