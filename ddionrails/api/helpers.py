"""This module exists as a separate module because enqueu refused to work while
run_import_on_redis was declared in ddionrails.api.views.webhooks
"""

from datetime import datetime

from django.core.cache import caches
from django.core.management import call_command
from django_rq.queues import enqueue

from config.settings.base import BACKUP_DIR
from ddionrails.imports.management.commands.update import update_single_study
from ddionrails.imports.manager import StudyImportManager
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket


def _clear_all_caches():
    caches["default"].clear()
    caches["instrument_api"].clear()
    caches["dataset_api"].clear()


def run_import_on_redis(study_name):
    """Queue Study import in redis queue that will in turn queue single import jobs"""
    study = Study.objects.get(name=study_name)
    manager = StudyImportManager(study, redis=True)
    file_name = f"webhook_backup{datetime.now():%Y_%m_%d_%__%H_%M_%S}.json"
    Basket.backup(study, file_name)
    update_single_study(study, local=False, clean_import=True, manager=manager)
    enqueue(call_command, "loaddata", BACKUP_DIR.joinpath(file_name).absolute())
    enqueue(_clear_all_caches)
    enqueue(call_command, "search_index", "--rebuild", "-f")
