import pathlib
from datetime import datetime

from django.contrib.auth.models import User

import djclick as click
from workspace.models import Basket, BasketVariable, Script
from workspace.resources import (
    BasketResource,
    BasketVariableExportResource,
    ScriptExportResource,
    UserResource,
)

# Create a directory for backup files
BACKUP_DIR = "local/backup"
today = datetime.today().date()
path = pathlib.Path.cwd() / BACKUP_DIR / str(today)
path.mkdir(parents=True, exist_ok=True)


def determine_model_and_resource(entity: str):
    """ Determine which model and export resource to use """
    if entity == "users":
        return User, UserResource
    if entity == "baskets":
        return Basket, BasketResource
    if entity == "scripts":
        return Script, ScriptExportResource
    if entity == "basket_variables":
        return BasketVariable, BasketVariableExportResource


def backup_entity(entity: str, format_: str):
    """ Backup data to file with given format """
    model, resource = determine_model_and_resource(entity)
    num_entries = model.objects.count()
    click.secho(f"Exporting {num_entries} {entity}", fg="green")
    dataset = resource().export()
    formatted = dataset.export(format_)
    filename = (path / entity).with_suffix("." + format_)
    with open(str(filename), "w") as f:
        f.write(formatted)


@click.command()
@click.option("-u", "--users", default=False, is_flag=True, help="Backup user data")
@click.option("-b", "--baskets", default=False, is_flag=True)
@click.option("-v", "--basket-variables", default=False, is_flag=True)
@click.option("-s", "--scripts", default=False, is_flag=True)
@click.option("-f", "--format", "format_", default="csv")
def command(
    users: bool, baskets: bool, basket_variables: bool, scripts: bool, format_: str
):
    if users:
        backup_entity("users", format_)

    if baskets:
        backup_entity("baskets", format_)

    if basket_variables:
        backup_entity("basket_variables", format_)

    if scripts:
        backup_entity("scripts", format_)

    # If no command line argument is given, backup all entities
    if any((users, baskets, basket_variables, scripts)) is False:
        backup_entity("users", format_)
        backup_entity("baskets", format_)
        backup_entity("basket_variables", format_)
        backup_entity("scripts", format_)
