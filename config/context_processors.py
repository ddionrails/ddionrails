# -*- coding: utf-8 -*-

""" Context Processors for ddionrails.studies app """

from typing import Dict

from django.core.handlers.wsgi import WSGIRequest

from config.settings.base import FEATURES


def server_features(_: WSGIRequest) -> Dict[str, str]:
    """Make SHOW_STATISTICS setting accessible"""
    feature_sets = ("limited", "extended")
    if FEATURES in feature_sets:
        return {"FEATURES": FEATURES}
    return {"FEATURES": "limited"}
