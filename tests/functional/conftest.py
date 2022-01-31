"""Fixtures for functional tests"""
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory
from typing import Generator

import pytest

TEST_FILES = Path("./tests/functional/test_data/").absolute()


@pytest.fixture(scope="class", name="tmp_dir")
def _tmp_dir(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    with TemporaryDirectory() as directory:
        setattr(request.cls, "data_dir", Path(directory).absolute())
        copytree(TEST_FILES, directory, dirs_exist_ok=True)
        yield
