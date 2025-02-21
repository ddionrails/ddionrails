# -*- coding: utf-8 -*-

""" "System" management command for ddionrails project """

from django.conf import settings
from django.core.management.base import BaseCommand

from ddionrails.imports.manager import system_import


class Command(BaseCommand):
    """Import study settings from git repository as management command."""

    help = """ Import system settings from GitHub

        call: python manage.py system
    """

    def handle(self, *args, **options):
        system_import()
        self.stdout.write(
            self.style.SUCCESS(
                f"System settings successfully imported."
            )
        )
