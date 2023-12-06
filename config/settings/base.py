# -*- coding: utf-8 -*-

""" Django settings for ddionrails project: Base settings for all environments """

import os
import tempfile
import uuid
from pathlib import Path

from config.helpers import parse_env_variable_dict

# Beta stage config flag
# ------------------------------------------------------------------------------

SHOW_STATISTICS = os.getenv("SHOW_STATISTICS") == "True"

# PROJECT CONFIGURATION
# ------------------------------------------------------------------------------
BASE_DIR = Path(os.getenv("DOCKER_APP_DIRECTORY", "/usr/src/app/"))
BASE_UUID = uuid.UUID(os.getenv("BASE_UUID", default=str(uuid.NAMESPACE_DNS)))

APPS_DIR = BASE_DIR.joinpath("ddionrails")

BACKUP_DIR = Path("/var/lib/ddionrails/backup/")
os.makedirs(BACKUP_DIR, exist_ok=True)

FEATURES = os.getenv("FEATURES", "limited")

if os.getenv("DJANGO_DEBUG") == "True":
    DEBUG = True
    STATICFILES_DIRS = (str(BASE_DIR.joinpath("static")),)
else:
    DEBUG = False
    STATIC_ROOT = os.getenv("STATIC_ROOT")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
EMAIL_HOST = "mail"
ALLOWED_HOSTS = tuple(os.getenv("ALLOWED_HOSTS", default="").split(","))
DEFAULT_FEEDBACK_TO_EMAIL = os.getenv("DEFAULT_FEEDBACK_TO_EMAIL", "paneldata.org@diw.de")
FEEDBACK_TO_EMAILS = parse_env_variable_dict(os.getenv("FEEDBACK_TO_EMAILS", ""))
WSGI_APPLICATION = "config.wsgi.application"

IMPORT_BRANCH = os.getenv("IMPORT_BRANCH", default="master")
SYSTEM_NAME = os.getenv("SYSTEM_NAME", default="system")
SYSTEM_REPO_URL = os.getenv(
    "SYSTEM_REPO_URL", default="https://github.com/paneldata/system.git"
)

MEDIA_ROOT = os.getenv("DJANGO_MEDIA_ROOT", default="/var/django/media")
os.makedirs(MEDIA_ROOT, exist_ok=True)
MEDIA_URL = "/media/"

STATISTICS_SERVER_URL = os.getenv("STATISTICS_SERVER_URL", "/statistics-server/")

# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/


# APP CONFIGURATION
# ------------------------------------------------------------------------------

DJANGO_APPS = (
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
)
THIRD_PARTY_APPS = (
    "crispy_forms",
    "crispy_bootstrap4",
    "django_elasticsearch_dsl",
    "django_extensions",
    "django_rq",
    "import_export",
    "markdown",
    "webpack_loader",
    "rest_framework",
)
LOCAL_APPS = (
    "ddionrails.api",
    "ddionrails.base",
    "ddionrails.concepts",
    "ddionrails.data",
    "ddionrails.imports",
    "ddionrails.instruments",
    "ddionrails.publications",
    "ddionrails.studies",
    "ddionrails.statistics",
    "ddionrails.workspace",
)
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ddionrails.studies.context_processors.studies_processor",
                "ddionrails.studies.context_processors.show_statistics",
                "config.context_processors.server_features",
            ]
        },
    }
]

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB", default=str(BASE_DIR.joinpath("db.sqlite3"))),
        "USER": os.getenv("POSTGRES_USER", default="user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", default="password"),
        "HOST": os.getenv("POSTGRES_HOST", default="localhost"),
        "PORT": os.getenv("POSTGRES_PORT", default="5432"),
    }
}

# DJANGO RQ
# ------------------------------------------------------------------------------
RQ_QUEUES = {"default": {"HOST": "redis", "PORT": 6379, "DB": 0, "DEFAULT_TIMEOUT": 2000}}

THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "easy_thumbnails.processors.filters",
)


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = "en-us"

USE_TZ = True
TIME_ZONE = "UTC"
# TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_L10N = True


# Misc

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = "/static/"

WEBPACK_LOADER = {
    "DEFAULT": {
        # 'CACHE': not DEBUG,
        "BUNDLE_DIR_NAME": "dist/",  # must end with slash
        "STATS_FILE": BASE_DIR.joinpath("webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
    "instrument_api": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "api",
        "OPTIONS": {"MAX_ENTRIES": 15},
    },
    "dataset_api": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "api",
        "OPTIONS": {"MAX_ENTRIES": 15},
    },
}

# Rest API config
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_RATES": {"sendmail": "10/day"},
}

# DDI on Rails: imports
# Please ensure to include a trailing slash "/" for the path definitions.

# This tmp folder is reused in .production
DJANGO_TMP = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
IMPORT_REPO_PATH = Path(os.getenv("IMPORT_REPO_PATH", default=DJANGO_TMP.name))

# Create IMPORT_REPO_PATH on disk if it does not exist
IMPORT_REPO_PATH.mkdir(parents=True, exist_ok=True)

IMPORT_SUB_DIRECTORY = "ddionrails/"

# Django RQ
RQ_SHOW_ADMIN_LINK = True

# Github (either "https" or "ssh")
GIT_PROTOCOL = "https"

SHELL_PLUS_PRE_IMPORTS = (("ddionrails.imports.manager", "*"),)

SERVER_EMAIL = "admin@paneldata.org"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", default="paneldata.org@diw.de")

CRISPY_TEMPLATE_PACK = "bootstrap4"

# https://django-import-export.readthedocs.io/en/latest/api_widgets.html?highlight=date#import_export.widgets.DateTimeWidget
DATETIME_INPUT_FORMATS = ("%Y-%m-%d %H:%M:%S %Z",)

APPEND_SLASH = True

# Django Elasticsearch DSL
# ------------------------------------------------------------------------------
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTIC_PASSWORD")

# Prefix for index names.
# Overwritten in testing settings to separate testings indices which get deleted a lot
ELASTICSEARCH_DSL_INDEX_PREFIX = os.getenv("ELASTICSEARCH_DSL_INDEX_PREFIX", "")
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/quickstart.html
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": (
            f"http://elastic:{ELASTICSEARCH_PASSWORD}@"
            f"{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"
        )
    }
}
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/settings.html#elasticsearch-dsl-autosync
ELASTICSEARCH_DSL_AUTOSYNC = False
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/settings.html#elasticsearch-dsl-index-settings
ELASTICSEARCH_DSL_INDEX_SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}
# https://django-elasticsearch-dsl.readthedocs.io/en/latest/settings.html#elasticsearch-dsl-parallel
ELASTICSEARCH_DSL_PARALLEL = True
