import pathlib

import djclick as click
import tablib
from import_export.formats.base_formats import CSV, JSON, YAML, TextFormat

from ddionrails.workspace.resources import determine_model_and_resource


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


def determine_import_format(format_: str) -> TextFormat:
    """ Determine which format to use for import """
    if format_ == "csv":
        return CSV
    if format_ == "json":
        return JSON
    if format_ == "yaml":
        return YAML


def restore_entity(entity: str, path: pathlib.Path, format_: str) -> None:
    """ Restore data from file in given path with given format """
    model, resource = determine_model_and_resource(entity, method="restore")
    filename = (path / entity).with_suffix("." + format_)
    try:
        with open(str(filename), "r") as f:
            data = f.read()
    except FileNotFoundError:
        click.secho(f"No backup to restore for {entity}", fg="red")
        return
    import_format = determine_import_format(format_)
    dataset = import_format().create_dataset(data)

    # Try to import the data in dry_run mode
    result = resource().import_data(dataset, dry_run=True)
    if result.has_errors():
        output = tablib.Dataset()
        output.headers = ["basket", "user", "email", "study", "dataset", "variable"]
        click.secho(f"Error while importing {entity} from {filename}", fg="red")
        for line, errors in result.row_errors():
            for error in errors:
                click.secho(
                    f"Error in line: {line}, {error.error}, {error.row}", fg="red"
                )
                output.append(error.row.values())
        log_file = path / "error_log.csv"
        with open(str(log_file), "w") as f:
            f.write(output.csv)
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
@click.option("-p", "--path", "path", default="local/backup")
def command(
    users: bool,
    baskets: bool,
    basket_variables: bool,
    scripts: bool,
    format_: str,
    path: str,
):

    if path == "local/backup":
        path = get_most_recent_backup_directory()

    path = pathlib.Path(path)

    if users:
        restore_entity("users", path, format_)

    if baskets:
        restore_entity("baskets", path, format_)

    if basket_variables:
        restore_entity("basket_variables", path, format_)

    if scripts:
        restore_entity("scripts", path, format_)

    # If no command line argument is given, backup all entities
    if any((users, baskets, basket_variables, scripts)) is False:
        restore_entity("users", path, format_)
        restore_entity("baskets", path, format_)
        restore_entity("basket_variables", path, format_)
        restore_entity("scripts", path, format_)
