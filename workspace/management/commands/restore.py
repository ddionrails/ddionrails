import pathlib

from django.contrib.auth.models import User

import djclick as click
from import_export.formats.base_formats import CSV, JSON, YAML
from workspace.models import Basket, BasketVariable, Script
from workspace.resources import (
    BasketResource,
    BasketVariableImportResource,
    ScriptImportResource,
    UserResource,
)


def get_most_recent_backup_directory():
    """ Get the most recent backup directory """
    try:
        paths = sorted(
            pathlib.Path("local/backup").iterdir(), key=lambda f: f.stat().st_mtime
        )
        return paths[-1]
    except (FileNotFoundError, IndexError):
        click.secho("No backup to restore", fg="red")
        exit()


path = get_most_recent_backup_directory()


def determine_model_and_resource(entity: str):
    """ Determine which model and export resource to use """
    if entity == "users":
        return User, UserResource
    if entity == "baskets":
        return Basket, BasketResource
    if entity == "scripts":
        return Script, ScriptImportResource
    if entity == "basket_variables":
        return BasketVariable, BasketVariableImportResource


def determine_import_format(format_):
    """ Determine which format to use for import """
    if format_ == "csv":
        return CSV
    if format_ == "json":
        return JSON
    if format_ == "yaml":
        return YAML


def restore_entity(entity: str, format_: str):
    """ Backup data to file with given format """
    model, resource = determine_model_and_resource(entity)
    filename = (path / entity).with_suffix("." + format_)
    try:
        with open(str(filename), "r") as f:
            data = f.read()
    except FileNotFoundError:
        click.secho("No backup to restore", fg="red")
    import_format = determine_import_format(format_)
    dataset = import_format().create_dataset(data)

    # Try to import the data in dry_run mode
    result = resource().import_data(dataset, dry_run=True)
    if result.has_errors():
        click.secho(f"Error while importing {entity}", fg="red")
    else:
        # Actually write the data to the database if no errors were encountered in dry run
        resource().import_data(dataset, dry_run=False)
        click.secho(
            f"Succesfully imported {len(dataset)} {entity} from {filename}", fg="green"
        )


@click.command()
@click.option("-u", "--users", default=False, is_flag=True, help="Restore user data")
@click.option("-b", "--baskets", default=False, is_flag=True)
@click.option("-v", "--basket-variables", default=False, is_flag=True)
@click.option("-s", "--scripts", default=False, is_flag=True)
@click.option("-f", "--format", "format_", default="csv")
def command(
    users: bool, baskets: bool, basket_variables: bool, scripts: bool, format_: str
):

    if users:
        restore_entity("users", format_)
