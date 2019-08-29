# pylint: disable=missing-docstring
import unittest

from ddionrails.base.helpers.html_builder import TableBuilder


class TestTableBuilder(unittest.TestCase):
    def test_build_table_header(self):
        self.assertTrue(callable(TableBuilder.build_table_header))
