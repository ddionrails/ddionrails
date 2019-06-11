# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import,used-before-assignment

""" Django settings for ddionrails project: Settings for development environment """

from .base import *

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

RQ_QUEUES = {
    "default": {"HOST": "redis", "PORT": 6379, "DB": 0, "DEFAULT_TIMEOUT": 360},
    "high": {
        "URL": os.getenv("REDISTOGO_URL", "redis://redis:6379/0"),  # If you're on Heroku
        "DEFAULT_TIMEOUT": 500,
    },
    "low": {"HOST": "redis", "PORT": 6379, "DB": 0},
}
