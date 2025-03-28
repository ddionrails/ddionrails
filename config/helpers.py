# -*- coding: utf-8 -*-

""" Helper functions and classes for ddionrails project """

from dataclasses import dataclass
from json import load
from pathlib import Path
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


@dataclass
class LanguageContainer:
    """Container for multilanguage imprint data to address in template."""

    en: str
    de: str


def read_imprint_file(
    file_path: str,
) -> tuple[str, str, LanguageContainer, LanguageContainer]:
    """Read imprint json for the base settings module."""
    output = ("", "", LanguageContainer(en="", de=""), LanguageContainer(en="", de=""))
    if not file_path:
        return output
    path_to_file = Path(file_path)
    if not path_to_file.absolute().exists():
        return output
    with open(path_to_file, "r", encoding="utf-8") as imprint_file:
        imprint_content = load(imprint_file)
        output = (
            imprint_content.get("institute", ""),
            imprint_content.get("contact", ""),
            LanguageContainer(
                en=imprint_content.get("institute_home", {"en": ""})["en"],
                de=imprint_content.get("institute_home", {"de": ""})["de"],
            ),
            LanguageContainer(
                en=imprint_content.get("privacy_policy", {"en": ""})["en"],
                de=imprint_content.get("privacy_policy", {"de": ""})["de"],
            ),
        )

    return output
