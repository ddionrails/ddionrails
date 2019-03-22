from .base import *  # noqa

WSGI_APPLICATION = "ddionrails.wsgi_hewing.application"

DEBUG = True

ALLOWED_HOSTS = ["hewing.soep.de", "ddionrails.soep.de"]

SYSTEM_NAME = "system"
SYSTEM_REPO_URL = "https://github.com/paneldata/system.git"

IMPORT_BRANCH = "development"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/tmp/dor-debug.log",
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


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR + "/templates"],
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

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = True
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"
