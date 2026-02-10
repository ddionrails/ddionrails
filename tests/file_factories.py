import json
from abc import ABC
from csv import DictWriter
from dataclasses import dataclass
from os import remove
from pathlib import Path
from shutil import rmtree
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper, mkdtemp
from typing import Any

from faker import Faker

FAKE = Faker()


@dataclass
class PatchKwargs:
    target: str
    return_value: Path

    def keys(self):
        return ["target", "return_value"]

    def __getitem__(self, item):
        return getattr(self, item)


def tmp_import_path() -> tuple[Path, PatchKwargs]:
    tmp_path = Path(mkdtemp())

    patch_dict = PatchKwargs(
        target="ddionrails.studies.models.Study.import_path",
        return_value=tmp_path,
    )
    return tmp_path, patch_dict


class _TMPImportFILE(ABC):

    file_name: Path
    tmp_path: Path
    import_path_patch_arguments: PatchKwargs

    def __init__(self) -> None:
        self.tmp_path, self.import_path_patch_arguments = tmp_import_path()
        super().__init__()

    def __del__(self):
        remove(self.file_name)
        rmtree(self.tmp_path)
        del self.tmp_path

    def __exit__(self):
        remove(self.file_name)
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
        """Can be put into a patch function to override the projects import path with parent_name"""
        return self.import_path_patch_arguments


class TMPJSON(_TMPImportFILE):

    def __init__(self, content: dict[Any, Any] | list[Any]):
        super().__init__()
        self.file_name = self.tmp_path.joinpath(FAKE.file_name(extension="json"))
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(content, file)


class TMPCSV(_TMPImportFILE):

    def __init__(self, content: list[dict[str, Any]]):
        self.file_name = self.tmp_path.joinpath(FAKE.file_name(extension="csv"))
        with open(self.file_name, "w", encoding="utf-8") as file:
            writer = DictWriter(file, fieldnames=content[0].keys())
            for row in content:
                writer.writerow(row)
