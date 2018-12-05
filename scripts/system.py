#!/usr/bin/env python

from imports.manager import SystemImportManager, Repository
from ddionrails.models import System
from django_rq import job

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
