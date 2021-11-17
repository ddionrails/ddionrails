""" Statistics import related tests. """
import unittest
from pathlib import Path

import pytest

from ddionrails.statistics.imports import statistics_import
from ddionrails.statistics.models import VariableStatistic
from ddionrails.studies.models import Study
from tests.data.factories import VariableFactory


@pytest.mark.usefixtures("tmp_import_path")
@pytest.mark.django_db
class TestStatisticsImport(unittest.TestCase):
    """ Statistics import related tests. """

    import_path: Path
    study: Study

    def test_statistics_import(self) -> None:
        """ Test basic functionality. """
        variables_file = self.import_path.joinpath("variables.csv")
        VariableFactory(name="some-variable")
        VariableFactory(name="some-other-variable")
        VariableFactory(name="some-third-variable")
        statistics_import(variables_file, self.study)
        self.assertEqual(16, VariableStatistic.objects.all().count())
        linked_variables = set()
        for statistic in VariableStatistic.objects.all():
            linked_variables.add(statistic.variable)
        self.assertEqual(3, len(linked_variables))
