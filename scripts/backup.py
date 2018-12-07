#!/usr/bin/env python

import django_rq

from ddionrails.models import Backup
from imports.manager import BackupImportManager, Repository


def run_backup():
    backup = Backup()
    repo = Repository(backup)
    repo.clone_repo()
    BackupImportManager(backup).run_import(import_all=True)


def run():
    django_rq.enqueue(run_backup)


if __name__ == "__main__":
    run()
