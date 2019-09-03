# -*- coding: utf-8 -*-

""" Pavement file for ddionrails project """

import pathlib
import sys

import django
from django.core import management
from django.db.utils import IntegrityError
from paver.easy import consume_args, needs, sh, task

sys.path.append(".")


@task
def docu():
    """Run the docu make script (no delete)."""
    sh("cd ../docs; make html")


@task
def full_docu():
    """Completely rebuild the docu."""
    sh("cd ../docs; rm -r _build; make html")


@task
def django_setup():
    """ Setup django for other tasks """
    django.setup()


@task
@needs("django_setup")
def create_admin():
    """Create superuser "admin" with password "test"."""
    from django.contrib.auth.models import User

    try:
        User.objects.create_superuser("admin", "admin@example.com", "test")
    except IntegrityError:
        # User "admin" already exists
        pass


@task
@needs("django_setup")
def reset_migrations():
    """Reset all migrations."""
    migration_files = pathlib.Path("ddionrails").glob("*/migrations/0*.py")
    for migration_file in migration_files:
        migration_file.unlink()
    management.call_command("makemigrations")


@task
@needs("django_setup")
def erd():
    """Create an entity relationship diagram """
    management.call_command(
        "graph_models", all_applications=True, outputfile="local/erd.png"
    )


@task
@needs("django_setup")
def migrate():
    """Make migrations and run migrate."""
    management.call_command("makemigrations")
    management.call_command("migrate")


@task
@needs("django_setup")
@consume_args
def test(args):
    """ Test the project without functional tests """
    sh(
        f"DJANGO_SETTINGS_MODULE=config.settings.testing pytest -rf -m 'not functional' {' '.join(args)}"
    )


@task
@needs("django_setup")
@consume_args
def functional_test(args):
    """ Test the project with functional tests """
    sh(
        f"DJANGO_SETTINGS_MODULE=config.settings.testing pytest -rf -m functional {' '.join(args)}"
    )
