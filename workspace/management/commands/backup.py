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


def backup_users(format_):
    """ Backup user data to file with given format """
    num_users = User.objects.count()
    click.secho(f"Exporting {num_users} users", fg="green")
    dataset = UserResource().export()
    formatted_users = dataset.export(format_)
    users_filename = (path / "users").with_suffix("." + format_)
    with open(str(users_filename), "w") as f:
        f.write(formatted_users)


def backup_baskets(format_):
    """ Backup baskets data to file with given format """
    num_baskets = Basket.objects.count()
    click.secho(f"Exporting {num_baskets} baskets", fg="green")
    dataset = BasketResource().export()
    formatted_baskets = dataset.export(format_)
    baskets_filename = (path / "baskets").with_suffix("." + format_)
    with open(str(baskets_filename), "w") as f:
        f.write(formatted_baskets)


def backup_basket_variables(format_):
    """ Backup basket variables data to file with given format """
    num_basket_variables = BasketVariable.objects.count()
    click.secho(f"Exporting {num_basket_variables} baskets variables", fg="green")
    dataset = BasketVariableExportResource().export()
    formatted_basket_variables = dataset.export(format_)
    basket_variables_filename = (path / "basket_variables").with_suffix("." + format_)
    with open(str(basket_variables_filename), "w") as f:
        f.write(formatted_basket_variables)


def backup_scripts(format_):
    """ Backup scripts data to file with given format """
    num_scripts = Script.objects.count()
    click.secho(f"Exporting {num_scripts} scripts", fg="green")
    dataset = ScriptExportResource().export()
    formatted_scripts = dataset.export(format_)
    scripts_filename = (path / "scripts").with_suffix("." + format_)
    with open(str(scripts_filename), "w") as f:
        f.write(formatted_scripts)


@click.command()
@click.option("-u", "--users", default=False, is_flag=True, help="Backup user data")
@click.option("-b", "--baskets", default=False, is_flag=True)
@click.option("-v", "--basket-variables", default=False, is_flag=True)
@click.option("-s", "--scripts", default=False, is_flag=True)
@click.option("-f", "--format", "format_", default="csv")
def command(users, baskets, basket_variables, scripts, format_):
    if users:
        backup_users(format_)

    if baskets:
        backup_baskets(format_)

    if basket_variables:
        backup_basket_variables(format_)

    if scripts:
        backup_scripts(format_)

    # If no command line argument is given, backup all entities
    if any((users, baskets, basket_variables, scripts)) is False:
        backup_users(format_)
        backup_baskets(format_)
        backup_basket_variables(format_)
        backup_scripts(format_)
