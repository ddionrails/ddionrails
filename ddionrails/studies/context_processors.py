# -*- coding: utf-8 -*-

""" Context Processors for ddionrails.studies app """

from typing import Dict

from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet

from .models import Study


# request is a required parameter
def studies_processor(
    request: WSGIRequest
) -> Dict[str, QuerySet]:  # pylint: disable=unused-argument
    """ Context processor returns all studies in a dictionary """

    return dict(studies=Study.objects.all().only("name", "label"))
