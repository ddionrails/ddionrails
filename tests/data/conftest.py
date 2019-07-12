# -*- coding: utf-8 -*-

""" Pytest fixtures """

import pytest


@pytest.fixture
def invalid_dataset_data():
    """ An invalid input for dataset forms and imports """
    return dict(dataset_name="")


@pytest.fixture
def valid_dataset_data(study):  # pylint: disable=unused-argument
    """ A valid input for dataset forms and imports, relates to study fixture """
    return dict(study=study.id, dataset_name="some-dataset")


@pytest.fixture
def invalid_variable_data(study):
    """ An invalid input for variable forms and imports, relates to study fixture """
    return dict(variable_name="", dataset_name="", study_object=study)


@pytest.fixture
def valid_variable_data(study):
    """ A valid input for variable forms and imports """
    return dict(
        variable_name="some-variable", dataset_name="some-dataset", study_object=study
    )
