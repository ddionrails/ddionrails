# -*- coding: utf-8 -*-
# pylint: disable=unused-argument,invalid-name

""" Pytest fixtures """

import pytest

from .factories import AttachmentFactory


@pytest.fixture
def attachment(db):
    """ An attachment in the database """
    return AttachmentFactory(url="https://some-url.org")
