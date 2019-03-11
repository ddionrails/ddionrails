import json
import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "django_extensions",
    "elasticsearch",
    "elasticsearch_dsl",
    "markdown",
    "django_rq",
    "webpack_loader",
    "import_export",
    "crispy_forms",
    # DDI on Rails
    "ddionrails",
    "concepts",
    "imports",
    "studies",
    "data",
    "elastic",
    "workspace",
    "instruments",
    "publications",
    "api",
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

ROOT_URLCONF = "ddionrails.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "studies.models.context",
            ]
        },
    }
]

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db/db.sqlite3"),
    }
}


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
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

WEBPACK_LOADER = {
    "DEFAULT": {
        # 'CACHE': not DEBUG,
        "BUNDLE_DIR_NAME": "dist/",  # must end with slash
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
    }
}

# DDI on Rails: imports
# Please ensure to include a trailing slash "/" for the path definitions.

IMPORT_REPO_PATH = "static/repositories/"
IMPORT_SUB_DIRECTORY = "ddionrails/"

# DDI on Rails: index

INDEX_HOST = "localhost"  # not used yet
INDEX_PORT = "9200"  # not used yet
INDEX_NAME = "dor"

# Django RQ
RQ_SHOW_ADMIN_LINK = True

# Github (either "https" or "ssh")
GIT_PROTOCOL = "https"

SHELL_PLUS_PRE_IMPORTS = (("imports.manager", "*"),)

SERVER_EMAIL = "admin@paneldata.org"
DEFAULT_FROM_EMAIL = "webmaster@paneldata.org"

# credit to "Two Scoops of Django 1.11", p. 55
# 5.4.1 Using JSON Files
SECRETS_FILE = os.path.join(BASE_DIR, "secrets.json")

with open(SECRETS_FILE) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    """ Get the secret variable or return explicit exception. """
    try:
        return secrets[setting]
    except KeyError:
        error_msg = ""
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_secret("SECRET_KEY")

CRISPY_TEMPLATE_PACK = "bootstrap3"


# https://django-import-export.readthedocs.io/en/latest/api_widgets.html?highlight=date#import_export.widgets.DateTimeWidget
DATETIME_INPUT_FORMATS = ("%Y-%m-%d %H:%M:%S %Z",)
