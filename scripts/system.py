#!/usr/bin/env python

from django_rq import job

from ddionrails.models import System
from imports.manager import Repository, SystemImportManager


@job
def run_system():
    system = System.get()
    repo = Repository(system)
    repo.update_or_clone_repo()
    SystemImportManager(system).run_import(import_all=True)


def run():
    run_system()


if __name__ == "__main__":
    run()
