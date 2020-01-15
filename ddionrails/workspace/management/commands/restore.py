# -*- coding: utf-8 -*-

""" Management command to restore user data for ddionrails.workspace app """

import pathlib
import sys

import djclick as click
import tablib

from ddionrails.workspace.resources import determine_model_and_resource


def get_recent_backup_directory():
    """ Get the most recent backup directory """
    try:
        paths = sorted(
            pathlib.Path("local/backup").iterdir(), key=lambda f: f.stat().st_mtime
        )
        return paths[-1]
    except (FileNotFoundError, IndexError):
        click.secho("No backup to restore", fg="red")
        sys.exit()


def restore_entity(entity: str, path: pathlib.Path, format_: str) -> None:
    """ Restore data from file in given path with given format """
    _, resource = determine_model_and_resource(entity, method="restore")
    filename = (path / entity).with_suffix("." + format_)
    try:
        with open(str(filename), "r") as infile:
            dataset = tablib.Dataset().load(infile.read())
    except FileNotFoundError:
        click.secho(f"No backup to restore for {entity}", fg="red")
        return

    # Try to import the data in dry_run mode
    result = resource().import_data(dataset, dry_run=True)
    if result.has_errors():
        output = tablib.Dataset()
        output.headers = ["basket", "user", "email", "study", "dataset", "variable"]
        click.secho(f"Error while importing {entity} from {filename}", fg="red")
        if result.row_errors():
            _print_errors(result.row_errors(), output)
        log_file = path / "error_log.csv"
        with open(str(log_file), "w") as outfile:
            outfile.write(output.export("csv"))
    else:
        # Actually write the data to the database if no errors were encountered in dry run
        resource().import_data(dataset, dry_run=False)
        click.secho(
            f"Succesfully imported {len(dataset)} {entity} from {filename}", fg="green"
        )


def _print_errors(error_information: tuple, dataset: tablib.Dataset):
    """Handle error output for restore_entity function"""
    for line, errors in error_information:
        for error in errors:
            click.secho(f"Error in line: {line}, {error.error}, {error.row}", fg="red")
            dataset.append(error.row.values())


@click.command()
@click.option("-u", "--users", default=False, is_flag=True, help="Restore user data")
@click.option("-b", "--baskets", default=False, is_flag=True)
@click.option("-v", "--basket-variables", default=False, is_flag=True)
@click.option("-s", "--scripts", default=False, is_flag=True)
@click.option("-f", "--format", "format_", default="csv")
@click.option("-p", "--path", "path", default="local/backup")
def command(  # pylint: disable=too-many-arguments
    users: bool,
    baskets: bool,
    basket_variables: bool,
    scripts: bool,
    format_: str,
    path: str,
):
    """ Restore user generated data """
    if path == "local/backup":
        path = get_recent_backup_directory()

    _path: pathlib.Path = pathlib.Path(path)

    if users:
        restore_entity("users", _path, format_)

    if baskets:
        restore_entity("baskets", _path, format_)

    if basket_variables:
        restore_entity("basket_variables", _path, format_)

    if scripts:
        restore_entity("scripts", _path, format_)

    # If no command line argument is given, backup all entities
    if any((users, baskets, basket_variables, scripts)) is False:
        restore_entity("users", _path, format_)
        restore_entity("baskets", _path, format_)
        restore_entity("basket_variables", _path, format_)
        restore_entity("scripts", _path, format_)
