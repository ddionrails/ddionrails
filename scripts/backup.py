#!/usr/bin/env python

from imports.manager import BackupImportManager, Repository
from ddionrails.models import Backup
import django_rq

def run_backup():
    backup = Backup()
    repo = Repository(backup)
    repo.clone_repo()
    BackupImportManager(backup).run_import(import_all=True)

def run():
    django_rq.enqueue(run_backup)

if __name__ == "__main__":
    run()
