"""Test imports from the instruments app."""
import unittest
from tempfile import TemporaryDirectory
from typing import Generator

import pytest

from ddionrails.instruments.imports import question_import_direct


@pytest.fixture(scope="class", name="tmp_dir")
def _tmp_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    with TemporaryDirectory() as directory:
        setattr(request.cls, "data_dir", directory.name)
        yield


@pytest.mark.usefixtures("tmp_dir")
class QuestionImport(unittest.TestCase):
    def test_import(self) -> None:
        ...
