# -*- coding: utf-8 -*-

""" "System" management command for ddionrails project """

from django.conf import settings
from django.core.management.base import BaseCommand

from ddionrails.base.models import System
from ddionrails.imports.manager import Repository, SystemImportManager


class Command(BaseCommand):
    """Import study settings from git repository as management command."""

    help = """ Import system settings from GitHub

        call: python manage.py system
    """

    def handle(self, *args, **options):
        system = System.get()
        repo = Repository(system)
        repo.pull_or_clone()
        SystemImportManager(system).run_import()
        self.stdout.write(
            self.style.SUCCESS(
                f"System settings succesfully imported from {settings.SYSTEM_REPO_URL}."
            )
        )
