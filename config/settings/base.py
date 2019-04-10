import os

import environ

BASE_DIR = environ.Path(__file__) - 3
APPS_DIR = BASE_DIR.path("ddionrails")

env = environ.Env()
DEBUG = env.bool("DJANGO_DEBUG", False)
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = tuple(env.list("ALLOWED_HOSTS", default=[]))
WSGI_APPLICATION = "config.wsgi.application"

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
    "django_extensions",
    "elasticsearch",
    "elasticsearch_dsl",
    "markdown",
    "django_rq",
    "webpack_loader",
    "import_export",
    "crispy_forms",
)
LOCAL_APPS = (
    "ddionrails.api",
    "ddionrails.base",
    "ddionrails.concepts",
    "ddionrails.data",
    "ddionrails.elastic",
    "ddionrails.imports",
    "ddionrails.instruments",
    "ddionrails.publications",
    "ddionrails.studies",
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
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ddionrails.studies.models.context",
            ]
        },
    }
]

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': os.getenv('POSTGRES_DB', default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('POSTGRES_USER', default='user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='password'),
        'HOST': os.getenv('POSTGRES_HOST', default='localhost'),
        "PORT": os.getenv('POSTGRES_PORT', default=5432)
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
STATICFILES_DIRS = (str(BASE_DIR.path("static")),)

WEBPACK_LOADER = {
    "DEFAULT": {
        # 'CACHE': not DEBUG,
        "BUNDLE_DIR_NAME": "dist/",  # must end with slash
        "STATS_FILE": BASE_DIR.path("webpack-stats.json"),
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

CRISPY_TEMPLATE_PACK = "bootstrap3"

# https://django-import-export.readthedocs.io/en/latest/api_widgets.html?highlight=date#import_export.widgets.DateTimeWidget
DATETIME_INPUT_FORMATS = ("%Y-%m-%d %H:%M:%S %Z",)
