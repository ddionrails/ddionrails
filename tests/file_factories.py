"""Factory to create temporary test files"""

import json
from abc import ABC
from csv import DictWriter
from dataclasses import dataclass
from os import remove
from pathlib import Path
from shutil import copytree, rmtree
from tempfile import mkdtemp
from typing import Any

from faker import Faker

FAKE = Faker()


@dataclass
class _PatchKwargs:
    target: str
    return_value: Path

    def keys(self):  # pylint: disable=missing-function-docstring
        return ["target", "return_value"]

    def __getitem__(self, item):
        return getattr(self, item)


def tmp_import_path(folder: Path | None = None) -> tuple[Path, _PatchKwargs]:
    """Take or create a tmp folder, return arguments to patch the global import path"""
    if folder is None:
        tmp_path = Path(mkdtemp())
    else:
        tmp_path = folder

    patch_dict = _PatchKwargs(
        target="ddionrails.studies.models.Study.import_path",
        return_value=tmp_path,
    )
    return tmp_path, patch_dict


def tmp_import_path_with_test_data() -> tuple[Path, _PatchKwargs]:
    """Move test data into patched import path"""
    csv_path = Path("./tests/functional/test_data/some-study/ddionrails/").absolute()
    tmp_path, patch_dict = tmp_import_path()
    copytree(csv_path, tmp_path, dirs_exist_ok=True)
    return tmp_path, patch_dict


def destroy_tmp_path(tmp_path: Path):
    """Use rmtree to remove directory."""
    tmp_path = Path(tmp_path)
    if tmp_path.exists():
        rmtree(tmp_path, ignore_errors=True)


class _TMPImportFILE(ABC):

    file_name: Path
    tmp_path: Path
    import_path_patch_arguments: _PatchKwargs
    folder_external: bool = False

    def __init__(self, folder: Path | None = None) -> None:
        if folder is not None:
            self.folder_external = True
        self.tmp_path, self.import_path_patch_arguments = tmp_import_path(folder)
        super().__init__()

    def __del__(self):
        if self.file_name.exists():
            remove(self.file_name)
        if not self.folder_external:
            rmtree(self.tmp_path)
        del self.tmp_path

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file_name.exists():
            remove(self.file_name)
        if not self.folder_external:
            rmtree(self.tmp_path)
        del self.tmp_path

    @property
    def name(self) -> Path:
        """Path to the temp file created"""
        return self.file_name

    @property
    def parent_name(self) -> Path:
        """Path to the folder containing the created file"""
        return self.tmp_path

    @property
    def import_patch_arguments(self):
        """Arguments to be used in patch function for system data import path"""
        return self.import_path_patch_arguments


class TMPJSON(_TMPImportFILE):
    """Creates and fills temporary JSON file"""

    def __init__(self, content: dict[Any, Any] | list[Any], file_name: str = ""):
        super().__init__()
        if file_name == "":
            file_name = FAKE.file_name(extension="json")
        self.file_name = self.tmp_path.joinpath(file_name)
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(content, file)


class TMPCSV(_TMPImportFILE):
    """Creates and fills temporary CSV file"""

    def __init__(
        self,
        content: list[dict[str, Any]],
        file_name: str = "",
        folder: Path | None = None,
    ):
        super().__init__(folder=folder)
        if file_name == "":
            file_name = FAKE.file_name(extension="csv")
        self.file_name = self.tmp_path.joinpath(file_name)
        with open(self.file_name, "w", encoding="utf-8") as file:
            writer = DictWriter(file, fieldnames=content[0].keys())
            writer.writeheader()
            for row in content:
                writer.writerow(row)
