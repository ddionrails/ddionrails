# -*- coding: utf-8 -*-

""" Mixins for ddionrails.workspace app """

from typing import Dict


class SoepMixin:  # pylint: disable=too-few-public-methods

    START_YEAR = 2001

    def _soep_year(self, year):
        letters = self._soep_letters()
        return letters[year - self.START_YEAR]

    @staticmethod
    def _soep_letters(page=None):
        a_num = ord("a")
        g_num = ord("g") + 1
        z_num = ord("z") + 1
        letters1 = [chr(x) for x in range(a_num, z_num)]
        letters2 = ["b" + chr(x) for x in range(a_num, g_num)]
        if page == 1:
            return letters1
        if page == 2:
            return letters2
        return letters1 + letters2

    def _soep_classify_dataset(self, dataset_name):
        letters = self._soep_letters()
        h_files = ["%sh" % l for l in letters]
        h_files = h_files + ["%shgen" % l for l in letters]
        h_files = h_files + ["%shost" % l for l in letters]
        h_files = h_files + ["%shausl" % l for l in letters]
        h_files = h_files + ["%shbrutto" % l for l in letters]
        p_files = ["%sp" % l for l in letters]
        p_files = p_files + ["%spgen" % l for l in letters]
        p_files = p_files + ["%spost" % l for l in letters]
        p_files = p_files + ["%spausl" % l for l in letters]
        p_files = p_files + ["%spbrutto" % l for l in letters]
        p_files = p_files + ["%skind" % l for l in letters]
        p_files = p_files + ["%spequiv" % l for l in letters]
        p_files = p_files + ["%spluecke" % l for l in letters]
        p_files = p_files + ["%sppage17" % l for l in letters]
        if dataset_name in h_files:
            return "h"
        if dataset_name in p_files:
            return "p"
        return "other"

    def _soep_letter_year(self) -> Dict[str, int]:
        letter_year = dict()
        letters = self._soep_letters()
        for index, letter in enumerate(letters):
            letter_year[letter] = self.START_YEAR + index
        letter_year[""] = 0
        return letter_year

    def _soep_get_year(self, dataset_name, letters=True):
        if dataset_name[0:2] in self._soep_letters(page=2):
            letter = dataset_name[0:2]
        elif dataset_name[0:1] in self._soep_letters(page=1):
            letter = dataset_name[0:1]
        else:
            letter = ""
        if letters:
            return letter
        return self._soep_letter_year()[letter]

    def _generate_script_dict(self) -> dict:
        script_dict = dict()
        for variable in self.basket.variables.all():
            dataset_name = variable.dataset.name
            if dataset_name not in script_dict.keys():
                script_dict[dataset_name] = self._create_dataset_dict(dataset_name)
            script_dict[dataset_name]["variables"].add(variable.name)
            for dataset_dict in script_dict.values():
                self._enrich_dataset_dict(dataset_dict)
        return script_dict

    def _create_dataset_dict(self, dataset_name: str) -> Dict:
        analysis_unit = self._soep_classify_dataset(dataset_name)
        return dict(
            name=dataset_name,
            analysis_unit=analysis_unit,
            period=self._soep_get_year(dataset_name, letters=False),
            prefix=self._soep_get_year(dataset_name),
            variables=set(),
        )

    @staticmethod
    def _enrich_dataset_dict(dataset_dict):
        dataset = dataset_dict
        analysis_unit = dataset["analysis_unit"]
        if analysis_unit == "h":
            dataset["matches"] = ["p", "h"]
            dataset["key"] = "%shhnr" % dataset["prefix"]
            dataset["variables"].add(dataset["key"])
        elif analysis_unit == "p":
            dataset["matches"] = ["p"]
            dataset["key"] = "persnr"
            dataset["variables"].add(dataset["key"])
            dataset["variables"].add("%shhnr" % dataset["prefix"])
        else:
            dataset["matches"] = []
            dataset["key"] = ""

    @staticmethod
    def _validate_datasets(script_dict, analysis_unit, valid=True):
        valid_list = []
        invalid_list = []
        for dataset_name, dataset_dict in script_dict.items():
            if analysis_unit in dataset_dict["matches"]:
                valid_list.append(dataset_name)
            else:
                invalid_list.append(dataset_name)
            for element in ["phrf", "ppfad"]:
                if element in invalid_list:
                    invalid_list.remove(element)
        if valid:
            return valid_list
        return invalid_list

    @staticmethod
    def _get_selected_years(script_dict):
        return {d["prefix"] for d in script_dict.values()}
