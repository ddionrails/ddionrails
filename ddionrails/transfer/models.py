"""Models for the transfer-server App."""
from django.db import models

from ddionrails.data.models.variable import Variable

# Create your models here.


class VariableStatistic(models.Model):
    """Stores CSV statistics Data for a data.Variable."""

    class PlotType(models.TextChoices):
        """Define possible plot types."""

        CATEGORICAL = "categorical", "Categorical"
        NUMERICAL = "numerical", "Numerical"
        ORDINAL = "ordinal", "Ordinal"

    # Keys
    id = models.AutoField(primary_key=True)
    variable = models.ForeignKey(to=Variable, null=False, on_delete=models.CASCADE)

    # Attributes
    plot_type = models.TextField(null=False, choices=PlotType.choices)
    statistics = models.TextField(null=False, blank=False)
    start_year = models.IntegerField(null=False, blank=False)
    end_year = models.IntegerField(null=False, blank=False)


class IndependentVariables(models.Model):
    """ Information about valuelabels for independent variables (dimensions)."""

    # Keys
    id = models.AutoField(primary_key=True)
    variable = models.ForeignKey(to=Variable, null=False, on_delete=models.CASCADE)

    labels = models.JSONField()
