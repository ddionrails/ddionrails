# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,no-self-use,too-few-public-methods

""" Test cases for helpers in ddionrails.config app """

import pytest

from config.helpers import RowHelper, lower_dict_names, render_markdown

md_text = """
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
        html = render_markdown(md_text)
        assert "<h1>" in html
        assert "<ul>" in html
        assert 'class="table"' in html

    def test_lower_dict_names(self):
        dictionary = dict(_name="NAME", othername="NAME")
        lower_dict_names(dictionary)
        assert dictionary["_name"] == "name"
        assert dictionary["othername"] == "NAME"

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_jekyll_reader(self):
        pytest.fail("Test not implemented yet")

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_script_list(self):
        pytest.fail("Test not implemented yet")

    @pytest.mark.skip(reason="no way of currently testing this")
    def script_list_output(self):
        pytest.fail("Test not implemented yet")


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
