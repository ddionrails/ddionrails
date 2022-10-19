# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import,used-before-assignment

""" Django settings for ddionrails project: Settings for development environment """

from pathlib import Path

import debug_toolbar

from config.settings.base import *  # pylint: disable=W0614
from config.settings.base import BASE_DIR, INSTALLED_APPS, MIDDLEWARE, TEMPLATES

debug_templates_path = Path(debug_toolbar.__file__).parent.joinpath("templates")

DEBUG = True
TEMPLATE_DEBUG = True

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ("debug_toolbar",)
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE = ("debug_toolbar.middleware.DebugToolbarMiddleware",) + MIDDLEWARE
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
INTERNAL_IPS = ("127.0.0.1",)

# credit to https://stackoverflow.com/a/50332425
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: True}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "local/debug.log",
        }
    },
    "loggers": {
        "django.request": {"handlers": ["file"], "level": "DEBUG", "propagate": True},
        "imports": {"handlers": ["file"], "level": "DEBUG", "propagate": True},
    },
}

del TEMPLATES[0]["APP_DIRS"]
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    (
        "django.template.loaders.filesystem.Loader",
        [BASE_DIR.joinpath("templates"), debug_templates_path],
    ),
    (
        "django.template.loaders.app_directories.Loader",
        [BASE_DIR.joinpath("templates"), debug_templates_path],
    ),
]
