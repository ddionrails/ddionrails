# -*- coding: utf-8 -*-

""" Context Processors for ddionrails.studies app """

from typing import Dict, List

from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet

from config.settings.base import SHOW_STATISTICS

from .models import Study


# request is a required parameter
def studies_processor(
    request: WSGIRequest,  # pylint: disable=unused-argument
) -> Dict[str, QuerySet[Study]]:
    """Context processor returns all studies in a dictionary"""

    return dict(studies=Study.objects.all().only("name", "label").order_by("label"))


def show_statistics(_: WSGIRequest) -> Dict[str, List[Study]]:
    """Make SHOW_STATISTICS setting accessible"""
    studies = []

    if SHOW_STATISTICS:
        studies = list(
            Study.objects.filter(datasets__variables__statistics_flag=True).distinct()
        )

    return {"STATISTICS_STUDIES": studies}
