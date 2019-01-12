import os
import subprocess

import yaml
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
    text = text.replace("<table>", "<table class=\"table\">")
    return(text)


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
    for key, value in dictionary.items():
        if "_name" in key:
            dictionary[key] = value.lower()


def jekyll_reader(text):
    lines = text.split("\n")
    yaml_lines = []
    line = lines.pop(0)
    if line == "---":
        while lines:
            line = lines.pop(0)
            if line in "---":
                break
            yaml_lines.append(line)
    else:
        lines.insert(0, line)
    yaml_content = "\n".join(yaml_lines)
    return dict(
        content="\n".join(lines),
        yaml_content=yaml_content,
        data=yaml.safe_load(yaml_content),
    )
