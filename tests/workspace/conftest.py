# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,invalid-name

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


@pytest.fixture(name="basket_variable")
def _basket_variable(request, db):
    """ A basket_variable in the database """
    _factory = BasketVariableFactory()
    if request.instance:
        request.instance.basket_variable_factory = _factory
    return _factory
