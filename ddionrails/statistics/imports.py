""" Import functions for statistical data used in data visualization."""

import json
from csv import DictReader
from glob import glob
from pathlib import Path
from typing import Dict, List, Tuple

from django.core.files import File
from django_rq import enqueue

from ddionrails.data.models.variable import Variable
from ddionrails.statistics.models import (
    IndependentVariable,
    StatisticsMetadata,
    VariableStatistic,
)
from ddionrails.studies.models import Study

CACHE: Dict[str, IndependentVariable] = {}


def statistics_import(file: Path, study: Study) -> None:
    """Import variable statistics."""
    VariableStatistic.objects.filter(variable__dataset__study=study).delete()
    with open(file, "r", encoding="utf8") as variables_file:
        variables = DictReader(variables_file)
        if "statistics" not in variables.fieldnames:  # type: ignore
            return None
        for variable in variables:
            if not variable["statistics"] == "True":
                continue
            # If meta.json is missing skip import
            try:
                _import_single_variable(variable, study)
            except FileNotFoundError:
                continue
    enqueue(_metadata_import, study)
    return None


def _metadata_import(study: Study) -> None:
    objects = []
    StatisticsMetadata.objects.filter(variable__dataset__study=study).delete()
    for variable in (
        Variable.objects.filter(dataset__study=study)
        .exclude(statistics_data=None)
        .prefetch_related("dataset")
    ):
        independent_variables = {}
        start_year = 0
        end_year = 0
        for statistic in variable.statistics_data.all():
            if not start_year or start_year > statistic.start_year:
                start_year = statistic.start_year
            if not end_year or end_year > statistic.end_year:
                end_year = statistic.end_year
            for independent_variable in statistic.independent_variables.all():
                independent_variables[independent_variable.id] = independent_variable
        metadata = StatisticsMetadata()
        metadata.variable = variable
        metadata.metadata = {
            "study": study.name,
            "title": variable.label_de,
            "variable": variable.name,
            "id": str(variable.id),
            "dataset": variable.dataset.name,
            "dimensions": [
                {
                    "variable": independent_variable.variable.name,
                    "label": independent_variable.variable.label_de,
                    "labels": independent_variable.labels,
                    "values": independent_variable.values,
                }
                for independent_variable in independent_variables.values()
            ],
            "start_year": start_year,
            "end_year": end_year,
        }
        objects.append(metadata)
    StatisticsMetadata.objects.bulk_create(objects, ignore_conflicts=True)


def _import_single_variable(variable: Dict[str, str], study: Study) -> None:
    """Import statistics data for a single defined value."""

    try:
        variable_object = Variable.objects.get(
            name=variable["name"], dataset__name=variable["dataset"], dataset__study=study
        )
    except Exception as error:
        raise ValueError(f"{variable}") from error
    import_base_path: Path = study.import_path().parent
    statistics_base_path = import_base_path.joinpath("statistics")
    if variable["type"] in ["numerical", "categorical"]:
        _import_single_type(variable_object, statistics_base_path, variable["type"])
    if variable["type"] == "ordinal":
        _import_single_type(variable_object, statistics_base_path, "numerical")
        _import_single_type(variable_object, statistics_base_path, "categorical")


def _import_independent_variables(path: Path) -> List[str]:
    with open(path.joinpath("meta.json"), "r", encoding="utf8") as metadata_file:
        independent_variable_metadata = json.load(metadata_file)
    if "dimensions" in independent_variable_metadata:
        independent_variable_metadata = independent_variable_metadata["dimensions"]
    independent_variable_names = []
    for datum in independent_variable_metadata:
        if datum["variable"] in CACHE:
            independent_variable_names.append(datum["variable"])
            continue
        # TODO: Temporary solution while metadata is incomplete
        # Change to specific retrieval when metadata changes.
        variable_object = Variable.objects.filter(name=datum["variable"]).first()
        try:
            independent_variable, _ = IndependentVariable.objects.get_or_create(
                labels=datum["labels"], values=datum["values"], variable=variable_object
            )
        except BaseException as error:
            raise BaseException(f"{datum}  {variable_object}") from error

        CACHE[datum["variable"]] = independent_variable
        independent_variable_names.append(datum["variable"])

    return independent_variable_names


def _import_single_type(variable: Variable, base_path: Path, stat_type: str) -> None:
    """Import alle statistics for a single value and of a single type."""
    statistics_path = base_path.joinpath(f"{stat_type}/{variable.name}")
    independent_variables = _import_independent_variables(statistics_path)
    files = glob(f"{statistics_path}/{variable.name}*.csv")
    for file in files:
        statistics = VariableStatistic()
        statistics.variable = variable
        statistics.plot_type = stat_type
        independent_variable_names = []
        for independent_variable in independent_variables:
            if independent_variable in file:
                independent_variable_names.append(independent_variable)
        statistics.set_independent_variable_names(independent_variable_names)
        # statistics.save() in _store_csv_data
        statistics.start_year, statistics.end_year = _get_start_and_end_year(Path(file))
        _store_csv_data(Path(file), statistics)
        for name in independent_variable_names:
            statistics.independent_variables.add(CACHE[name])
        statistics.save()


def _get_start_and_end_year(file_path) -> Tuple[int, int]:
    with open(file_path, "r", encoding="utf8") as file:
        file.seek(0)
        reader = DictReader(file)
        years = set()
        for line in reader:
            years.add(line["year"])

        return (int(min(years)), int(max(years)))


def _store_csv_data(file_path: Path, statistics: VariableStatistic) -> None:
    """Get content and limited metadata from a csv statistics file."""
    with open(file_path, "r", encoding="utf8") as file:
        file.seek(0)
        statistics.statistics.save(
            file_path.name + "/" + file_path.parent.parent.name, File(file)
        )
        statistics.save()
