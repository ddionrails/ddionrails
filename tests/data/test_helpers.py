# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,no-self-use

""" Test cases for helpers in ddionrails.data app """

import pytest

from ddionrails.data.helpers import LabelTable
from tests.concepts.factories import PeriodFactory

from .factories import DatasetFactory, VariableFactory


@pytest.fixture
def variables(db):  # pylint: disable=unused-argument,invalid-name
    """ This fixture contains two variables from two datasets from two periods
        they appear in an unsorted order
    """
    dataset = DatasetFactory(name="d1")
    other_dataset = DatasetFactory(name="d2")
    period = PeriodFactory(name="2019")
    other_period = PeriodFactory(name="2018")
    variable = VariableFactory(name="v1")
    other_variable = VariableFactory(name="v2")
    dataset.period = period
    other_dataset.period = other_period
    variable.dataset = dataset
    other_variable.dataset = other_dataset
    return [variable, other_variable]


@pytest.fixture
def label_table(variables):
    """ A label table with the variables from the variables fixture """
    return LabelTable(variables)


class TestLabelTable:
    def test_init_method(self, variables):
        """ The init method of the label table sorts the variables by their datasets periods """
        label_table = LabelTable(variables)
        variables.reverse()
        assert label_table.variables == variables

    def test_init_method_without_period(self, variables):
        """ The first variable has no period in this test """
        variables[0].dataset.period = None
        label_table = LabelTable(variables)
        assert label_table.variables == variables

    def test_to_dict_method(self, mocker, variables):
        label_table = LabelTable(variables)
        mocked_fill_header = mocker.patch.object(LabelTable, "_fill_header")
        mocked_fill_body = mocker.patch.object(LabelTable, "_fill_body")
        label_table.to_dict()
        mocked_fill_header.assert_called_once()
        mocked_fill_body.assert_called_once()

    def test_simplify_label_method(self, label_table):
        label = "some-label"
        output = label_table._simplify_label(label)  # pylint: disable=protected-access
        assert output == label

    def test_simplify_label_method_with_non_string_label(self, label_table):
        label = 1
        output = label_table._simplify_label(label)  # pylint: disable=protected-access
        expected = ""
        assert output == expected
