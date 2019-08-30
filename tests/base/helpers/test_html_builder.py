""" Test functionality related to building html Fragments. """
import re
import unittest
from random import randint

from ddionrails.base.helpers.html_builder import TableBuilder


class TestTableBuilder(unittest.TestCase):
    """ Test Functionality related to table creation. """

    ALPHA_START = 97
    ALPHA_END = 122

    def _random_alphabetical_string(self):
        _length = randint(7, 10)  # nosec
        _string = ""
        for _ in range(3, _length):
            _string = _string + chr(randint(self.ALPHA_START, self.ALPHA_END))  # nosec
        return _string

    def test_build_table_header(self):
        """ Can we get a html table header from a list input """
        # Does our function exist?
        self.assertTrue(callable(TableBuilder.build_table_header))
        test_input = [
            self._random_alphabetical_string(),
            self._random_alphabetical_string(),
        ]
        expected = "<tr><th>{}</th><th>{}</th></tr>".format(*test_input)
        result = TableBuilder.build_table_header(test_input)
        # Is The structure as expected?
        # Not caring about whitespaces here.
        self.assertEqual(expected, re.sub(r"\s+", "", result))
