import djclick as click

from ddionrails.base.models import System
from ddionrails.imports.manager import Repository, SystemImportManager


@click.command()
def command():
    """ Import system settings from GitHub

        call: python manage.py system
    """
    system = System.get()
    repo = Repository(system)
    repo.update_or_clone_repo()
    SystemImportManager(system).run_import(import_all=True)
