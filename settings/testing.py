import logging

import django_rq.queues
from fakeredis import FakeRedis, FakeStrictRedis

from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

INSTALLED_APPS.remove("django_extensions")

WSGI_APPLICATION = "ddionrails.wsgi.application"

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

SYSTEM_NAME = "system"
SYSTEM_REPO_URL = "https://github.com/ddionrails/test-system.git"
BACKUP_NAME = "backup"
BACKUP_REPO_URL = "https://github.com/ddionrails/test-backup.git"
IMPORT_BRANCH = "master"
INDEX_NAME = "testing"

logging.disable(logging.CRITICAL)

RQ_QUEUES = {"default": {"HOST": "localhost", "PORT": 6379, "DB": 0, "DEFAULT_TIMEOUT": 360, "ASYNC": False}}

# https://github.com/rq/django-rq/issues/277#issuecomment-391555883
# Credit to @zyv, adapted from https://github.com/rq/django-rq/issues/106#issuecomment-367674954
django_rq.queues.get_redis_connection = lambda _, strict: FakeStrictRedis() if strict else FakeRedis()
