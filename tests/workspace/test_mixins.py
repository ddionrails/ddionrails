# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,invalid-name
# pylint: disable=protected-access

""" Test cases for mixins in ddionrails.workspace app """

import pytest

from ddionrails.workspace.mixins import SoepMixin


@pytest.fixture(name="soepmixin")
def _soepmixin():
    return SoepMixin()


@pytest.fixture(name="script_dict")
def _script_dict():
    return {
        "bah": dict(
            name="bah",
            analysis_unit="h",
            period=2010,
            prefix="ba",
            variables=set(),
            matches=["p", "h"],
        ),
        "rp": dict(
            name="rp",
            analysis_unit="p",
            period=2001,
            prefix="r",
            variables=set(),
            matches=["p"],
        ),
    }


class TestSoepMixin:
    def test_enrich_dataset_dict_method(self, soepmixin):
        dataset_dict_p = {
            "analysis_unit": "p",
            "variables": set(),
            "merge_id": "",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }
        soepmixin._enrich_dataset_dict(dataset_dict_p)
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
        soepmixin._enrich_dataset_dict(dataset_dict_h)
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
        soepmixin._enrich_dataset_dict(dataset_dict_other)
        assert dataset_dict_other == {
            "analysis_unit": "",
            "variables": set(),
            "merge_id": "",
            "prefix": "ba",
            "curr_hid": "bahhnr",
        }

    @pytest.mark.usefixtures("db", "script_metadata")
    def test_validate_datasets_method(self, script_dict, soepmixin):
        analysis_unit_p = "p"
        valid_p = soepmixin._validate_datasets(script_dict, analysis_unit_p)
        analysis_unit_h = "h"
        valid_h = soepmixin._validate_datasets(script_dict, analysis_unit_h)

        assert valid_p == ["bah", "rp"]
        assert valid_h == ["bah"]
