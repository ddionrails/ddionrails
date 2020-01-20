# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods,no-self-use,invalid-name

""" Test cases for helpers in ddionrails.data app """

from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

import pytest

from ddionrails.data.helpers import LabelTable
from tests.concepts.factories import PeriodFactory

from .factories import DatasetFactory, VariableFactory


@pytest.fixture(name="variables")
def _variables(db):  # pylint: disable=unused-argument,invalid-name
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


@pytest.fixture(name="label_table")
def _label_table(variables):
    """ A label table with the variables from the variables fixture """
    return LabelTable(variables)


class TestLabelTable:
    def test_init_method(self, variables):
        """LabelTables Init should sort passed variables by their datasets periods."""
        # Save teh variables to get their period data from the dataset.
        for variable in variables:
            variable.save()
        label_table = LabelTable(variables)
        variables.reverse()
        assert label_table.variables == variables

    def test_label_render_limit(self, variables):
        """LabelTable should not be rendered for variable with more than 100 labels.

        The creation of the HTML of the LabelTable is to time consuming for large
        numbers of labels.
        """

        categories = list()
        for number in range(0, 101):
            categories.append({"label": uuid4(), "value": number})

        # To use unittest assertions with this pytest setup.
        # Class should be refactored to inherit TestCase if time can be allocated.
        test = TestCase()

        with patch(
            "ddionrails.data.models.variable.Variable.get_categories",
            return_value=categories,
        ):
            label_table = LabelTable(variables)
            test.assertFalse(label_table.render_table)
            test.assertEqual("", label_table.to_html())

    def test_variable_render_limit(self, variables):
        """LabelTable should not be rendered for more than 100 variables.

        The creation of the HTML of the LabelTable is to time consuming for large
        numbers of related variables.
        """

        # To use unittest assertions with this pytest setup.
        # Class should be refactored to inherit TestCase if time can be allocated.
        test = TestCase()

        for _ in range(0, 100):
            variables.append(variables[0])
        label_table = LabelTable(variables)
        # Do not render a LabelTable if variable count exceeds the limit.
        test.assertFalse(label_table.render_table)
        # Throw away all variables for the LabelTable if their number exceeds
        # the limit.
        test.assertEqual(list(), label_table.variables)

    def test_to_html(self, variables):
        """LabelTable should not be rendered for variable with more than 100 labels.

        The creation of the HTML of the LabelTable is to time consuming for large
        numbers of labels.
        """

        categories = list()
        for number in range(0, 5):
            categories.append({"label": uuid4(), "value": number})

        test = TestCase()

        with patch(
            "ddionrails.data.models.variable.Variable.get_categories",
            return_value=categories,
        ):
            label_table = LabelTable(variables)
            html_output = label_table.to_html()
            for variable in variables:
                test.assertIn(variable.name, html_output)

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
