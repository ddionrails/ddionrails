""" Define import test specific fixtures. """
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import mkdtemp
from typing import Generator
from unittest.mock import patch

import pytest

from ddionrails.studies.models import Study


@pytest.fixture()
def tmp_import_path(
    request: pytest.FixtureRequest, study: Study
) -> Generator[None, None, None]:
    """ Stage import test data in tmp folder. """
    tmp_path = Path(mkdtemp())
    csv_path = Path("tests/imports/test_data/").absolute()
    import_path = copytree(csv_path, tmp_path.joinpath("ddionrails"))

    patch_dict = {
        "target": "ddionrails.studies.models.Study.import_path",
        "return_value": import_path,
    }

    if request.instance:
        request.instance.patch_argument_dict = patch_dict
        request.instance.import_path = import_path
        request.instance.study = study

    with patch(**patch_dict):
        yield

    rmtree(tmp_path)
