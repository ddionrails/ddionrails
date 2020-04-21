# -*- coding: utf-8 -*-

""" Management command to restore user data for ddionrails.workspace app """

import pathlib
import sys

import tablib
from django.core.management.base import BaseCommand

from ddionrails.workspace.resources import determine_model_and_resource


class Command(BaseCommand):
    "Restore user generated data."

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
        if path == "local/backup":
            path = self.get_recent_backup_directory()

        _path: pathlib.Path = pathlib.Path(path)

        if users:
            self.restore_entity("users", _path, _format)

        if baskets:
            self.restore_entity("baskets", _path, _format)

        if basket_variables:
            self.restore_entity("basket_variables", _path, _format)

        if scripts:
            self.restore_entity("scripts", _path, _format)

        # If no command line argument is given, backup all entities
        if any((users, baskets, basket_variables, scripts)) is False:
            self.restore_entity("users", _path, _format)
            self.restore_entity("baskets", _path, _format)
            self.restore_entity("basket_variables", _path, _format)
            self.restore_entity("scripts", _path, _format)

    def log_success(self, message: str):
        """Log success messages."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message: str):
        """Log error messages."""
        self.stderr.write(self.style.ERROR(message))

    def get_recent_backup_directory(self):
        """ Get the most recent backup directory """
        try:
            paths = sorted(
                pathlib.Path("local/backup").iterdir(), key=lambda f: f.stat().st_mtime
            )
            return paths[-1]
        except (FileNotFoundError, IndexError):
            self.log_error("No backup to restore")
            sys.exit()

    def restore_entity(self, entity: str, path: pathlib.Path, _format: str) -> None:
        """ Restore data from file in given path with given format """
        _, resource = determine_model_and_resource(entity, method="restore")
        filename = (path / entity).with_suffix("." + _format)
        try:
            with open(str(filename), "r") as infile:
                dataset = tablib.Dataset().load(infile.read())
        except FileNotFoundError:
            self.log_error(f"No backup to restore for {entity}")
            return

        # Try to import the data in dry_run mode
        result = resource().import_data(dataset, dry_run=True)
        if result.has_errors():
            output = tablib.Dataset()
            output.headers = ["basket", "user", "email", "study", "dataset", "variable"]
            self.log_error(f"Error while importing {entity} from {filename}")
            if result.row_errors():
                self._print_errors(result.row_errors(), output)
            log_file = path / "error_log.csv"
            with open(str(log_file), "w") as outfile:
                outfile.write(output.export("csv"))
        else:
            # Actually write the data to the database
            # if no errors were encountered in dry run
            resource().import_data(dataset, dry_run=False)
            self.log_success(
                f"Successfully imported {len(dataset)} {entity} from {filename}"
            )

    def _print_errors(self, error_information: tuple, dataset: tablib.Dataset):
        """Handle error output for restore_entity function"""
        for line, errors in error_information:
            for error in errors:
                self.log_error(f"Error in line: {line}, {error.error}, {error.row}")
                dataset.append(error.row.values())
