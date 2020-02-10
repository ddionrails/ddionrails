# -*- coding: utf-8 -*-
# pylint: disable=wildcard-import,unused-wildcard-import,used-before-assignment

""" Django settings for ddionrails project: Settings for testing environment """

import logging

from config.settings.base import *

TEMPLATE_DEBUG = False

# INSTALLED_APPS.remove("django_extensions")

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

SYSTEM_REPO_URL = "https://github.com/ddionrails/test-system.git"

logging.disable(logging.CRITICAL)

RQ_QUEUES = {
    "default": {
        "HOST": "redis",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": 360,
        "ASYNC": False,
    }
}

# Django Elasticsearch DSL
# ------------------------------------------------------------------------------
ELASTICSEARCH_DSL_INDEX_PREFIX = "testing_"
