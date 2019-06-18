# -*- coding: utf-8 -*-
# pylint: disable=unused-argument

""" Pytest fixtures """

import pytest

from .factories import BasketVariableFactory, ScriptFactory


@pytest.fixture
def script(db):
    """ A script in the database """
    return ScriptFactory(
        name="some-script",
        label="Some Script",
        settings='{"analysis_unit": "some-analysis-unit"}',
    )


@pytest.fixture
def basket_variable(db):
    """ A basket_variable in the database """
    return BasketVariableFactory()
