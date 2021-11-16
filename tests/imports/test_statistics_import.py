""" Statistics import related tests. """
import unittest
from pathlib import Path

import pytest

from ddionrails.statistics.imports import statistics_import
from ddionrails.statistics.models import VariableStatistic
from ddionrails.studies.models import Study


@pytest.mark.usefixtures("tmp_import_path")
class TestStatisticsImport(unittest.TestCase):
    """ Statistics import related tests. """

    import_path: Path
    study: Study

    def test_statistics_import(self) -> None:
        """ Test basic functionality. """
        # TODO
        statistics_import(self.import_path, self.study)
