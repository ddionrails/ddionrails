# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for helpers in ddionrails.config app """

from config.helpers import RowHelper, lower_dict_names, render_markdown

MD_TEXT = """
# heading

text text

* eins
* zwei

| x | y |
|---|---|
| 1 | 2 |
| 3 | 4 |
"""


class TestHelpers:
    def test_render_markdown(self):
        html = render_markdown(MD_TEXT)
        assert "<h1>" in html
        assert "<ul>" in html
        assert 'class="table"' in html

    def test_lower_dict_names(self):
        dictionary = dict(_name="NAME", othername="NAME")
        lower_dict_names(dictionary)
        assert dictionary["_name"] == "name"
        assert dictionary["othername"] == "NAME"


class TestRowHelper:
    def test_row_method(self):
        row_helper = RowHelper()
        expected = False
        assert expected is row_helper.row()

    def test_row_method_true(self):
        """ Everytime row is called, row_index is incremented.
            If it hits 4, it returns True
        """
        row_helper = RowHelper()
        row_helper.row_index = 3
        expected = True
        assert expected is row_helper.row()

    def test_reset_method(self):
        row_helper = RowHelper()
        row_helper.row_index = 1
        row_helper.reset()
        expected = 0
        assert expected == row_helper.row_index
