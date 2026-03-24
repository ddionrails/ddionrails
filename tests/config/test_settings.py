# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name

"""Test cases for settings of ddionrails project"""

from importlib import reload
from unittest.mock import patch

from django.test.testcases import LiveServerTestCase

from config.settings import base


class TestDebugSettings(LiveServerTestCase):

    def test_django_debug_settings(self):
        expected_debug = True

        with patch.dict("os.environ", {"DJANGO_DEBUG": str(expected_debug)}):
            reload(base)
            self.assertEqual(expected_debug, base.DEBUG)
            self.assertFalse(hasattr(base, "STATIC_ROOT"))
            self.assertEqual(
                (str(base.BASE_DIR.joinpath("static")),), base.STATICFILES_DIRS
            )

    def test_django_debug_settings_false(self):
        expected_debug = False
        expected_static_root = "static"

        with patch.dict(
            "os.environ",
            {"DJANGO_DEBUG": str(expected_debug), "STATIC_ROOT": expected_static_root},
        ):
            reload(base)

            self.assertEqual(expected_debug, base.DEBUG)
            self.assertEqual(expected_static_root, base.STATIC_ROOT)
