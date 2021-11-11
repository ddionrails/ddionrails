""" Statistics import related tests. """
import unittest
from pathlib import Path

import pytest

from ddionrails.studies.models import Study
from ddionrails.transfer.imports import statistics_import


@pytest.mark.usefixtures("tmp_import_path")
class TestStatisticsImport(unittest.TestCase):
    """ Statistics import related tests. """

    import_path: Path
    study: Study

    def test_statistics_import(self) -> None:
        """ Test basic functionality. """
        # TODO
        statistics_import(self.import_path, self.study)
