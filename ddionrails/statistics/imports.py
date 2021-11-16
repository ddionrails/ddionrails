""" Import functions for statistical data used in data visualization."""
from pathlib import Path

from ddionrails.studies.models import Study


def statistics_import(file: Path, study: Study):
    """ Import variable statistics."""
    # TODO
    import_base_path: Path = study.import_path()
    statistics_base_path = import_base_path.joinpath("statistic")

    ...
