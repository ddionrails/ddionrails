import json
from pathlib import Path

from ddionrails.studies.models import Study
from ddionrails.workspace.models.script_metadata import ScriptMetadata


def script_metadata_import(file: Path, study: Study) -> None:
    with open(file, mode="r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)
        metadata_object = ScriptMetadata(study=study, data=metadata)
        metadata_object.save()
