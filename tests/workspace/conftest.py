# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,invalid-name

""" Pytest fixtures """

from csv import DictReader
from io import StringIO

import pytest
import urllib3

from ddionrails.studies.models import Study
from ddionrails.workspace.models.script_metadata import ScriptMetadata

from .factories import BasketVariableFactory, ScriptFactory


@pytest.fixture(name="script_metadata_dict", scope="session")
def _metadata_dict():
    metadata = {}
    manager = urllib3.PoolManager()
    file_content = StringIO(
        manager.request(
            "GET",
            (
                "https://raw.githubusercontent.com/paneldata/"
                "soep-core/v37/metadata/script_metadata.csv"
            ),
        ).data.decode("utf-8")
    )
    reader = DictReader(file_content)
    for line in reader:
        metadata[line["dataset_name"]] = line
    return metadata


@pytest.fixture(name="script_metadata")
def _script_metadata(script_metadata_dict):
    study = Study(name="soep-core")
    study.save()

    metadata_object = ScriptMetadata(study=study, metadata=script_metadata_dict)
    metadata_object.save()

    metadata_object = ScriptMetadata(study=study, metadata=script_metadata_dict)
    metadata_object.save()


@pytest.fixture
def script(db):
    """A script in the database"""
    return ScriptFactory(
        name="some-script",
        label="Some Script",
        settings='{"analysis_unit": "some-analysis-unit"}',
    )


@pytest.fixture(name="basket_variable")
def _basket_variable(request, db):
    """A basket_variable in the database"""
    _factory = BasketVariableFactory()
    if request.instance:
        request.instance.basket_variable_factory = _factory
    return _factory
