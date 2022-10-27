""" Workspace import functionality. """
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
            typed_line = line.copy()
            typed_line["is_matchable"] = (
                typed_line["is_matchable"].lower().strip() == "true"
            )
            typed_line["is_special"] = typed_line["is_special"].lower().strip() == "true"
            typed_line["syear"] = int(typed_line["syear"])
            metadata[line["dataset_name"]] = typed_line
    metadata_object = ScriptMetadata(study=study, metadata=metadata)
    metadata_object.save()
