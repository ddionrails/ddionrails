from csv import DictReader
from pathlib import Path

from ddionrails.studies.models import Study
from ddionrails.workspace.models.script_metadata import ScriptMetadata


def script_metadata_import(file: Path, study: Study) -> None:
    """Parse and import script metadata file"""
    metadata = {}
    with open(file, mode="r", encoding="utf-8") as file_content:
        reader = DictReader(file_content)
        for line in reader:
            metadata[line["dataset_name"]] = line
    metadata_object = ScriptMetadata(study=study, metadata=metadata)
    metadata_object.save()
