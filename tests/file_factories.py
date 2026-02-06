import json
from abc import ABC
from csv import DictWriter
from os import remove
from pathlib import Path
from shutil import rmtree
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper, mkdtemp
from typing import Any

from faker import Faker

FAKE = Faker()


def tmp_import_path() -> tuple[Path, dict[str, str]]:
    tmp_path = Path(mkdtemp())

    patch_dict = {
        "target": "ddionrails.studies.models.Study.import_path",
        "return_value": tmp_path,
    }
    return tmp_path, patch_dict


class _TMPFILE(ABC):

    file: _TemporaryFileWrapper

    def __del__(self):
        self.file.close()
        remove(self.file.name)
        del self.file

    def __exit__(self):
        self.file.close()
        remove(self.file.name)
        del self.file

    @property
    def name(self):
        self.file.name


class _TMPImportFILE(ABC):

    file_name: Path
    tmp_path: Path
    import_path_patch_arguments: dict[str, str]

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
    def name(self):
        return self.file_name

    @property
    def import_patch_arguments(self):
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
