# -*- coding: utf-8 -*-

""" Management command to backup user data for ddionrails.workspace app """

import pathlib
from datetime import datetime

from django.core.management.base import BaseCommand

from ddionrails.workspace.resources import determine_model_and_resource


class Command(BaseCommand):
    """ Backup user generated data """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("-u", "--users", action="store_true", default=False)
        parser.add_argument("-b", "--baskets", action="store_true", default=False)
        parser.add_argument(
            "-V", "--basket-variables", action="store_true", default=False
        )
        parser.add_argument("-s", "--scripts", action="store_true", default=False)
        parser.add_argument("-f", "--format", default="csv")
        parser.add_argument("-p", "--path", default="local/backup")
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        users = options["users"]
        baskets = options["baskets"]
        basket_variables = options["basket_variables"]
        scripts = options["scripts"]
        _format = options["format"]
        path = options["path"]
        path = self.create_backup_directory(pathlib.Path(path))

        if users:
            self.backup_entity("users", path, _format)

        if baskets:
            self.backup_entity("baskets", path, _format)

        if basket_variables:
            self.backup_entity("basket_variables", path, _format)

        if scripts:
            self.backup_entity("scripts", path, _format)

        # If no command line argument is given, backup all entities
        if any((users, baskets, basket_variables, scripts)) is False:
            self.backup_entity("users", path, _format)
            self.backup_entity("baskets", path, _format)
            self.backup_entity("basket_variables", path, _format)
            self.backup_entity("scripts", path, _format)

    def log_success(self, message: str):
        """Log success messages."""
        self.stdout.write(self.style.SUCCESS(message))

    def backup_entity(self, entity: str, path: pathlib.Path, format_: str) -> None:
        """ Backup data to file with given format """
        model, resource = determine_model_and_resource(entity, method="backup")
        num_entries = model.objects.count()
        self.log_success(f"Exporting {num_entries} {entity}")
        dataset = resource().export()
        formatted = dataset.export(format_)
        filename = (path / entity).with_suffix("." + format_)
        with open(str(filename), "w") as outfile:
            outfile.write(formatted)

    @staticmethod
    def create_backup_directory(base_dir: pathlib.Path) -> pathlib.Path:
        """Create a directory for backup files inside of base_dir"""
        today = datetime.today().date()
        path = pathlib.Path.cwd() / base_dir / str(today)
        path.mkdir(parents=True, exist_ok=True)
        return path
