# -*- coding: utf-8 -*-

""" Mixins for ddionrails.workspace app """

from typing import Dict

from ddionrails.workspace.scripts.soep_datasets import SoepDatasets


class SoepMixin:
    """SoepMixin - utilities/helpers to get SOEP years and year prefixes"""

    def _generate_script_dict(self):
        """ Map variables from basket to their dataset names """
        script_dict = dict()
        for variable in self.basket.variables.all():
            dataset_name = variable.dataset.name
            if dataset_name not in script_dict.keys():
                script_dict[dataset_name] = self._create_dataset_dict(dataset_name)
            script_dict[dataset_name]["variables"].add(variable.name)
            for dataset_dict in script_dict.values():
                self._enrich_dataset_dict(dataset_dict)
        return script_dict

    @staticmethod
    def _create_dataset_dict(dataset_name: str) -> Dict:
        """
        Returns dict with dataset information
        """
        dataset = SoepDatasets().get_dict(dataset_name)
        return dict(
            name=dataset_name,
            analysis_unit=dataset["analyse_unit"],
            period=dataset["syear"],
            prefix=dataset["prefix"],
            is_matchable=dataset["is_matchable"],
            is_special=dataset["is_special"],
            curr_hid=dataset["curr_hid"],
            variables=set(),
        )

    @staticmethod
    def _enrich_dataset_dict(dataset_dict):
        """
        Set merge_id variables and add variables to dataset
        """

        analysis_unit = dataset_dict["analysis_unit"]
        if analysis_unit == "h":
            dataset_dict["merge_id"] = dataset_dict["curr_hid"]
            dataset_dict["variables"].add(dataset_dict["curr_hid"])
        elif analysis_unit == "p":
            dataset_dict["merge_id"] = "persnr"
            dataset_dict["variables"].add("persnr")
            if dataset_dict["curr_hid"] != "":
                dataset_dict["variables"].add(dataset_dict["curr_hid"])
        else:
            dataset_dict["merge_id"] = ""

    @staticmethod
    def _validate_datasets(script_dict, analysis_unit, valid=True):
        """
        Validate if datasets from basket are in the datafiles.json

        Valid datasets:
        - Datasets that are included in datafiles.json
        - Datasets with prefixes
        - if household level: hhrf and hpfad
        - if private level: phrf and ppfad

        Invalid datasets:
        - Datasets that are not included in datafiles.json
        - Datasets without prefixes
        - if household level: phrf and ppfad and all datasets with analyse_unit == "p"
        - if private level: hhrf and hpfad
        """
        valid_list = []
        invalid_list = []

        all_datasets = SoepDatasets().data.keys()

        for dataset_name in script_dict.keys():
            if dataset_name in all_datasets:
                if script_dict[dataset_name]["prefix"] != "":
                    if (
                        analysis_unit == "h"
                        and script_dict[dataset_name]["analysis_unit"] == "p"
                    ):
                        invalid_list.append(dataset_name)
                    else:
                        valid_list.append(dataset_name)
                elif analysis_unit == "p" and dataset_name in {"phrf", "ppfad"}:
                    valid_list.append(dataset_name)
                elif analysis_unit == "h" and dataset_name in {"hhrf", "hpfad"}:
                    valid_list.append(dataset_name)
                else:
                    invalid_list.append(dataset_name)
            else:
                invalid_list.append(dataset_name)

        if valid:
            return valid_list
        return invalid_list
