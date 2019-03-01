import pathlib
from datetime import datetime

import djclick as click
from workspace.resources import determine_model_and_resource


def create_backup_directory(base_dir: pathlib.Path) -> pathlib.Path:
    # Create a directory for backup files inside of base_dir
    today = datetime.today().date()
    path = pathlib.Path.cwd() / base_dir / str(today)
    path.mkdir(parents=True, exist_ok=True)
    return path


def backup_entity(entity: str, path: pathlib.Path, format_: str) -> None:
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
@click.option("-p", "--path", "path", default="local/backup")
def command(
    users: bool,
    baskets: bool,
    basket_variables: bool,
    scripts: bool,
    format_: str,
    path: str,
):

    path = create_backup_directory(pathlib.Path(path))

    if users:
        backup_entity("users", path, format_)

    if baskets:
        backup_entity("baskets", path, format_)

    if basket_variables:
        backup_entity("basket_variables_export", path, format_)

    if scripts:
        backup_entity("scripts_export", path, format_)

    # If no command line argument is given, backup all entities
    if any((users, baskets, basket_variables, scripts)) is False:
        backup_entity("users", path, format_)
        backup_entity("baskets", path, format_)
        backup_entity("basket_variables_export", path, format_)
        backup_entity("scripts_export", path, format_)
