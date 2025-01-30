# -*- coding: utf-8 -*-

""" Functionality to help with development. """

import os
import pathlib
import sys
from argparse import ArgumentParser

import django
from django.core import management
from django.db.utils import IntegrityError
from pytest import main

sys.path.append(".")


def parse_args():
    parser: ArgumentParser = ArgumentParser(
        prog="project management shortcuts",
        description="Offer collection of command shortcuts for this project.",
    )
    functions = [
        "django_setup",
        "create_admin",
        "reset_migrations",
        "database_graph",
        "migrate",
        "integration_test",
    ]
    subparsers = parser.add_subparsers()
    test_parser = subparsers.add_parser("unit_test")
    command_parser = subparsers.add_parser("run")
    test_parser.add_argument("test_arguments", nargs="*")

    command_parser.add_argument("command_name", choices=functions)
    arguments = parser.parse_args(sys.argv[1:])
    if "test_arguments" in arguments:
        unit_test(arguments.test_arguments)
    if "command_name" in arguments:
        globals()[arguments.command_name]()


def django_setup():
    """Setup django for other tasks"""
    django.setup()


def create_admin():
    """Create superuser "admin" with password "test"."""
    django_setup()
    from django.contrib.auth.models import User

    try:
        User.objects.create_superuser("admin", "admin@example.com", "test")
    except IntegrityError:
        # User "admin" already exists
        pass


def reset_migrations():
    """Reset all migrations."""
    django_setup()
    migration_files = pathlib.Path("ddionrails").glob("*/migrations/0*.py")
    for migration_file in migration_files:
        migration_file.unlink()
    management.call_command("makemigrations")


def database_graph():
    """Create an entity relationship diagram"""
    django_setup()
    management.call_command(
        "graph_models", all_applications=True, outputfile="local/erd.png"
    )


def migrate():
    """Make migrations and run migrate."""
    django_setup()
    management.call_command("makemigrations")
    management.call_command("migrate")


def unit_test(custom_arguments):
    """Test the project without functional tests"""
    django_setup()
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.testing"
    main(["-rf", "-m", "not functional", *custom_arguments])


def integration_test():
    """Test the project with functional tests"""
    django_setup()
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.testing"
    main(["-rf", "-m", "functional"])


if __name__ == "__main__":
    parse_args()
