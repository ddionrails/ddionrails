"""This module exists as a separate module because enqueu refused to work while
run_import_on_redis was declared in ddionrails.api.views.webhooks
"""

from ddionrails.imports.management.commands.update import update_single_study
from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study


def run_import_on_redis(study_name):
    """Queue Study import in redis queue that will in turn queue single import jobs"""
    study = Study.objects.get(name=study_name)
    manager = StudyImportManager(study, redis=True)
    update_single_study(study, local=False, clean_import=True, manager=manager)
