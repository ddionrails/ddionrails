""" Import functions for statistical data used in data visualization."""
import json
from csv import DictReader
from glob import glob
from pathlib import Path
from typing import Dict, Tuple

from ddionrails.data.models.variable import Variable
from ddionrails.statistics.models import IndependentVariables, VariableStatistic
from ddionrails.studies.models import Study

CACHE = set()


def statistics_import(file: Path, study: Study) -> None:
    """ Import variable statistics."""
    with open(file, "r", encoding="utf8") as variables_file:
        variables = DictReader(variables_file)
        for variable in variables:
            if variable["statistics"] == "False":
                continue
            _import_single_variable(variable, study)


def _import_single_variable(variable: Dict[str, str], study: Study) -> None:
    """ Import statistics data for a single defined value. """

    variable_object = Variable.objects.get(
        name=variable["name"], dataset__name=variable["dataset"], dataset__study=study
    )
    import_base_path: Path = study.import_path()
    statistics_base_path = import_base_path.joinpath("statistics")
    if variable["type"] in ["numerical", "categorical"]:
        _import_single_type(variable_object, statistics_base_path, variable["type"])
    if variable["type"] == "ordinal":
        _import_single_type(variable_object, statistics_base_path, "numerical")
        _import_single_type(variable_object, statistics_base_path, "categorical")


def _import_independent_variables(path: Path) -> None:
    with open(path.joinpath("meta.json"), "r", encoding="utf8") as metadata_file:
        independent_variable_metadata = json.load(metadata_file)
    for datum in independent_variable_metadata:
        if datum["variable"] in CACHE:
            continue
        variable_object = Variable.objects.filter(name=datum["variable"]).first()
        independent_variable = IndependentVariables()
        independent_variable.labels = datum["values"]
        independent_variable.variable = variable_object
        independent_variable.save()
        CACHE.add(datum["variable"])


def _import_single_type(variable: Variable, base_path: Path, stat_type: str) -> None:
    """ Import alle statistics for a single value and of a single type. """
    statistics_path = base_path.joinpath(f"{stat_type}/{variable.name}")
    _import_independent_variables(statistics_path)
    files = glob(f"{statistics_path}/{variable.name}*.csv")
    for file in files:
        statistics = VariableStatistic()
        statistics.variable = variable
        statistics.plot_type = stat_type
        start_year, end_year, data = _get_csv_data(file)
        statistics.start_year = start_year
        statistics.end_year = end_year
        statistics.statistics = data
        statistics.save()


def _get_csv_data(file_path: str) -> Tuple[int, int, str]:
    """ Get content and limited metadata from a csv statistics file. """
    with open(file_path, "r", encoding="utf8") as file:
        output = file.read()
        file.seek(0)
        reader = DictReader(file)
        years = set()
        for line in reader:
            years.add(int(line["year"]))
    return min(years), max(years), output
