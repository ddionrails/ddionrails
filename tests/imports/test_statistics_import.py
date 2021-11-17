""" Statistics import related tests. """
import unittest
from pathlib import Path

import pytest

from ddionrails.statistics.imports import statistics_import
from ddionrails.statistics.models import IndependentVariables, VariableStatistic
from ddionrails.studies.models import Study
from tests.data.factories import VariableFactory


@pytest.mark.usefixtures("tmp_import_path")
@pytest.mark.django_db
class TestStatisticsImport(unittest.TestCase):
    """ Statistics import related tests. """

    import_path: Path
    study: Study

    def setUp(self) -> None:
        VariableFactory(name="some-variable")
        VariableFactory(name="some-other-variable")
        VariableFactory(name="some-third-variable")
        return super().setUp()

    def test_statistics_import(self) -> None:
        """ Test basic functionality. """
        variables_file = self.import_path.joinpath("variables.csv")
        statistics_import(variables_file, self.study)
        self.assertEqual(16, VariableStatistic.objects.all().count())
        linked_variables = set()
        for statistic in VariableStatistic.objects.all():
            linked_variables.add(statistic.variable)
        self.assertEqual(3, len(linked_variables))

    def test_independent_variable_import(self) -> None:
        """ Test import of linked independent variables. """
        VariableFactory(name="alter_gr")
        VariableFactory(name="sex")
        VariableFactory(name="bula_h")
        VariableFactory(name="bildungsniveau")
        VariableFactory(name="sampreg")
        VariableFactory(name="migback")
        variables_file = self.import_path.joinpath("variables.csv")
        statistics_import(variables_file, self.study)
        self.assertEqual(6, IndependentVariables.objects.all().count())
