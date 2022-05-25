# -*- coding: utf-8 -*-

""" Helper functions and classes for ddionrails project """


from typing import Dict

from django.utils.html import escape
from markdown import markdown


def render_markdown(markdown_text: str) -> str:
    """Render string to markdown."""
    try:
        markdown_text = escape(markdown_text)
        html = markdown(markdown_text, extensions=["markdown.extensions.tables"])
        html = html.replace("<table>", '<table class="table">')
    # The markdown.markdown function used by render markdown can potentially
    # raise these errors. But I did not find any input, that triggered errors.
    # They also exclude these except blocks from coverage themselves.
    except UnicodeDecodeError:  # pragma: no cover
        html = ""
    except ValueError:  # pragma: no cover
        html = ""
    return str(html)


def lower_dict_names(dictionary):
    """Lowercase all values of keys containing "_name" in the given dictionary"""
    for key, value in dictionary.items():
        if "_name" in key:
            dictionary[key] = value.lower()


class RowHelper:
    """A row helper class to help formatting HTML tables"""

    def __init__(self, number_of_rows=4):
        self.row_index = 0
        self.number_of_rows = number_of_rows

    def row(self) -> bool:
        """Returns True if the current row index is divisible by the number of rows"""
        self.row_index += 1
        return bool(self.row_index % self.number_of_rows == 0)

    def reset(self) -> str:
        """Resets the row index and returns an empty string"""
        self.row_index = 0
        return ""


def parse_env_variable_dict(env_variable: str) -> Dict[str, str]:
    """Parse pseudo dictionary env string into dictionary."""
    output = {}
    key_value_pairs = env_variable.strip().split(",")
    for pair in key_value_pairs:
        pair_list = pair.split(":")
        if len(pair_list) != 2 or "" in pair_list:
            return {}
        output[pair_list[0].strip()] = pair_list[1].strip()

    return output
