#!/usr/bin/env python

import django_rq
from django.conf import settings

from concepts.models import Concept
from imports.manager import Repository, StudyImportManager
from studies.models import Study


def clone_study_repos():
    for study in Study.objects.all():
        repo = Repository(study)
        repo.update_or_clone_repo()


def run_studies():
    for study in Study.objects.all():
        print("-------- Start study import --------")
        StudyImportManager(study).run_import(import_all=True)
        print("-------- End study import --------")
        if study.id == Study.objects.last().id:
            print("[INFO] Last study, start index")
            django_rq.enqueue(Concept.index_all)  #!!!!


def run():
    django_rq.enqueue(clone_study_repos)
    django_rq.enqueue(run_studies)


if __name__ == "__main__":
    run()
