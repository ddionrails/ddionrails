# -*- coding: utf-8 -*-

""" Context Processors for ddionrails.studies app """

from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet

from .models import Study


# request is a required parameter
def studies_processor(
    request: WSGIRequest  # pylint: disable=unused-argument
) -> Dict[str, QuerySet]:
    """ Context processor returns all studies in a dictionary """

    return dict(studies=Study.objects.all().only("name", "label"))
