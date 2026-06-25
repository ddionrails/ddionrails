# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name
# pylint: disable=protected-access

"""Test cases for mixins in ddionrails.workspace app"""

from django.test import TestCase

from ddionrails.workspace.mixins import SoepMixin
from ddionrails.workspace.models.script_metadata import ScriptMetadata
from tests.model_factories import BasketFactory, StudyFactory

SCRIPT_METADATA = {
    "bah": [
        {
            "dataset_name": "bah",
            "syear": "",
            "prefix": "",
            "analysis_unit": "p",
            "is_matchable": "",
            "curr_hid": "",
            "is_special": "",
        },
        {
            "dataset_name": "bah",
            "syear": "",
            "prefix": "",
            "analysis_unit": "h",
            "is_matchable": "",
            "curr_hid": "",
            "is_special": "",
        },
    ],
    "rp": [
        {
            "dataset_name": "rp",
            "syear": "",
            "prefix": "",
            "analysis_unit": "p",
            "is_matchable": "",
            "curr_hid": "",
            "is_special": "",
        }
    ],
}


class TestSoepMixin(TestCase):

    def setUp(self) -> None:
        study = StudyFactory(name="soep-core")
        basket = BasketFactory(study=study)

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()

        metadata_object = ScriptMetadata(study=basket.study, metadata=SCRIPT_METADATA)
        metadata_object.save()
        self.script_metadata = metadata_object

        self.soepmixin = SoepMixin()
        self.script_dict = {
            "bah": {
                "name": "bah",
                "analysis_unit": "h",
                "period": 2010,
                "prefix": "ba",
                "variables": set(),
                "matches": ["p", "h"],
            },
            "bah": {
                "name": "bah",
                "analysis_unit": "h",
                "period": 2010,
                "prefix": "ba",
                "variables": set(),
                "matches": ["p", "h"],
            },
            "rp": {
                "name": "rp",
                "analysis_unit": "p",
                "period": 2001,
                "prefix": "r",
                "variables": set(),
                "matches": ["p"],
            },
        }
        return super().setUp()

    def test_enrich_dataset_dict_method(self):
        dataset_dict_p = {
            "analysis_unit": "p",
            "variables": set(),
            "merge_id": "",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }
        self.soepmixin._enrich_dataset_dict(dataset_dict_p)
        assert dataset_dict_p == {
            "analysis_unit": "p",
            "variables": {"pid", "bahhnr"},
            "merge_id": "pid",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }

        dataset_dict_h = {
            "analysis_unit": "h",
            "variables": set(),
            "merge_id": "",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }
        self.soepmixin._enrich_dataset_dict(dataset_dict_h)
        assert dataset_dict_h == {
            "analysis_unit": "h",
            "variables": {"bahhnr"},
            "merge_id": "bahhnr",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }

        dataset_dict_other = {
            "analysis_unit": "",
            "variables": set(),
            "merge_id": "",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }
        self.soepmixin._enrich_dataset_dict(dataset_dict_other)
        assert dataset_dict_other == {
            "analysis_unit": "",
            "variables": set(),
            "merge_id": "",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }

    def test_validate_datasets_method(self):
        analysis_unit_p = "p"
        valid_p = self.soepmixin._validate_datasets(self.script_dict, analysis_unit_p)
        analysis_unit_h = "h"
        valid_h = self.soepmixin._validate_datasets(self.script_dict, analysis_unit_h)

        assert valid_p == ["bah", "rp"]
        assert valid_h == ["bah"]
