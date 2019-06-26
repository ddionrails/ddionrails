# -*- coding: utf-8 -*-

""" Helper functions and classes for ddionrails project """

import os
import subprocess

from django.utils.html import escape
from markdown import markdown


def render_markdown(text):
    """
    Render string to markdown. In the template, it is still necessary
    to indicate that this string is "safe".

    This is a wrapper for whatever markdown package is used in DDI on Rails,
    which might change over time. Currently, we use markdown.py.
    """
    text = escape(text)
    text = markdown(text, extensions=["markdown.extensions.tables"])
    text = text.replace("<table>", '<table class="table">')
    return text


def script_list(script):
    """
    Takes a list of shell commands and runs them.
    """
    script = "\n".join(script)
    os.system(script)


def script_list_output(script):
    """
    Takes a list of shell commands and runs them.

    Unlike script_list(), this command returns the output.
    """
    result = subprocess.check_output("\n".join(script), shell=True)
    return result.decode()


def lower_dict_names(dictionary):
    """ Lowercase all values of keys containing "_name" in the given dictionary """
    for key, value in dictionary.items():
        if "_name" in key:
            dictionary[key] = value.lower()


class RowHelper:
    """ A row helper class to help formatting HTML tables """

    def __init__(self, number_of_rows=4):
        self.row_index = 0
        self.number_of_rows = number_of_rows

    def row(self) -> bool:
        """ Returns True if the current row index is divisible by the number of rows """
        self.row_index += 1
        return bool(self.row_index % self.number_of_rows == 0)

    def reset(self) -> str:
        """ Resets the row index and returns an empty string """
        self.row_index = 0
        return ""
