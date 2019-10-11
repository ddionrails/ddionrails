# pylint: disable=invalid-name,missing-docstring,redefined-builtin
import os
import sys

import django

sys.path.insert(0, os.path.abspath("/usr/src/app"))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.base"
django.setup()

# -- Project information -----------------------------------------------------

project = "ddionrails"
copyright = "2019, Dominique Hansen"
author = "Dominique Hansen"

# The full version, including alpha/beta/rc tags
release = "4.1.2"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.napoleon", "sphinx.ext.autodoc", "sphinx.ext.autosummary"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "default"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

napoleon_google_docstring = True
