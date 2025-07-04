# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

""" Test cases for "python manage.py backup" """

import pytest
from django.test import TestCase

pytestmark = [pytest.mark.django_db]  # pylint: disable=invalid-name


class TestBasketBackup(TestCase):
    def test_backup(self): ...
