#!/usr/bin/python3
"""
Example:
# from soep_datasets import SoepDatasets

# test = SoepDatasets("bp")
# test.syear
1985
# test.prefix
b

TODO: Complete this description ..

TODO: add methodes and functions documenations ..

TODO: Add checks and exceptions ..

"""

import json
from os import path
from typing import Dict, Union

from ddionrails.workspace.models.script_metadata import ScriptMetadata

############################################################
# File   : soep_datasets.py
# Date   : 2020-02-04 / ISO 8601: YYYY-MM-DD
# Author : mpahl
############################################################

############################################################
# imports


############################################################


class SoepDatasetsJsonLoader:
    """class SoepDatasetsJsonLoader -
    utility class to load SoepDatasets from a json file

    returns json/dict data
    """

    @staticmethod
    def load_json_data(json_file):

        _json_data = {}

        if path.exists(json_file):
            with open(json_file, mode="r", encoding="utf-8") as file:
                _json_data = json.load(file)

        return _json_data


class SoepDataset:
    """
    TODO: Describe this module and methodes ..
    """

    def __init__(self):
        self.sub_path = ""
        self.syear = ""
        self.prefix = ""
        self.analyse_unit = ""
        self.is_matchable = ""


class SoepDatasets:
    """
    TODO: Describe this module and methodes ..
    """

    # Default path to json file
    # _default_json_datasets_file = "../datafiles.json" # bash tests
    _default_json_datasets_file = "ddionrails/workspace/datafiles.json"  # local tests
    # _default_json_datasets_file = "ddionrails/workspace/datafiles_with_long.json"

    ########################################################
    def __init__(self):

        self.data = ScriptMetadata.objects.get(study__name="soep-core").metadata

    def get_dict(self, dataset_name) -> Union[Dict[str, str], Dict]:
        """Return dataset information

        Returns:
            The dataset information from the datafiles.json file
            or an empty dictionairy if dataset_name is not present in JSON file.
        """
        return self.data.get(dataset_name, dict())

    def get_dataset(self, dataset_name):
        dataset_property = self.get_dict(dataset_name)

        _dataset = SoepDataset()

        _dataset.sub_path = dataset_property["sub_path"]
        _dataset.syear = dataset_property["syear"]
        _dataset.prefix = dataset_property["prefix"]
        _dataset.analyse_unit = dataset_property["analyse_unit"]
        _dataset.is_matchable = dataset_property["_is_matchable"]

        return _dataset


if __name__ == "__main__":

    TEST_DATASET = "bap"
    x = SoepDatasets()
    data_dict = x.get_dict(TEST_DATASET)
    data_object = x.get_dataset(TEST_DATASET)
