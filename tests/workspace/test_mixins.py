# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods,invalid-name

""" Test cases for mixins in ddionrails.workspace app """

import string

import pytest

from ddionrails.workspace.mixins import SoepMixin


@pytest.fixture
def soepmixin():
    return SoepMixin()


@pytest.fixture
def soepletters():
    return [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "ba",
        "bb",
        "bc",
        "bd",
        "be",
        "bf",
        "bg",
    ]


testdata_soep_classify_dataset_method = [("ah", "h"), ("ap", "p")]


class TestSoepMixin:
    def test_soep_year_method(self, soepmixin):
        year = 2001
        soepmixin._soep_year(year)  # pylint: disable=protected-access

    def test_soep_letters_method(self, soepmixin, soepletters):
        result = soepmixin._soep_letters()  # pylint: disable=protected-access
        assert result == soepletters

    def test_soep_letters_method_page_1(self, soepmixin):
        page = 1
        result = soepmixin._soep_letters(page)  # pylint: disable=protected-access
        expected = list(string.ascii_lowercase)
        assert result == expected

    def test_soep_letters_method_page_2(self, soepmixin):
        page = 2
        result = soepmixin._soep_letters(page)  # pylint: disable=protected-access
        assert result == ["ba", "bb", "bc", "bd", "be", "bf", "bg"]

    @pytest.mark.parametrize("argument,expected", testdata_soep_classify_dataset_method)
    def test_soep_classify_dataset_method(
        self, mocker, soepmixin, soepletters, argument, expected
    ):
        mocked_soep_letters = mocker.patch.object(SoepMixin, "_soep_letters")
        mocked_soep_letters.return_value = soepletters
        dataset_name = argument
        result = soepmixin._soep_classify_dataset(  # pylint: disable=protected-access
            dataset_name
        )
        assert result == expected

    def test_soep_letter_year_method(self, soepmixin):
        result = soepmixin._soep_letter_year()  # pylint: disable=protected-access
        assert result.get("") == 0
        assert result.get("a") == 2001
        assert result.get("z") == 2026
        assert result.get("bg") == 2033
