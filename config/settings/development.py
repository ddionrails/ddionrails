from .base import *  # noqa

WSGI_APPLICATION = "config.wsgi.application"

DEBUG = True

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ("debug_toolbar",)
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE = ("debug_toolbar.middleware.DebugToolbarMiddleware",) + MIDDLEWARE
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
INTERNAL_IPS = ("127.0.0.1",)

SYSTEM_NAME = "system"
SYSTEM_REPO_URL = "https://github.com/ddionrails/test-system.git"

IMPORT_BRANCH = "master"

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
    "default": {"HOST": "localhost", "PORT": 6379, "DB": 0, "DEFAULT_TIMEOUT": 360},
    "high": {
        "URL": os.getenv(
            "REDISTOGO_URL", "redis://localhost:6379/0"
        ),  # If you're on Heroku
        "DEFAULT_TIMEOUT": 500,
    },
    "low": {"HOST": "localhost", "PORT": 6379, "DB": 0},
}
