# -*- coding: utf-8 -*-

import re

from django.shortcuts import get_object_or_404, render

from ddionrails.studies.models import Study

from .helpers import parse_results, simple_search

NAMESPACE_REG = "namespace:[\"']?([a-z0-9-]*)"


def search(request):
    """Search for a simple search term"""
    q = request.GET.get("q", "")
    if q != "":
        results = simple_search(q)
    else:
        results = []
    try:
        study_name = re.search(NAMESPACE_REG, q).group(1)
        study = get_object_or_404(Study, name=study_name)
        template = "base_study.html"
    except:
        study = None
        template = "base.html"
    hits = parse_results(results)
    context = dict(
        q=q,
        study=study,
        template=template,
        results=results,
        hits=hits,
        has_hits=len(hits) > 0,
    )
    return render(request, "elastic/search.html", context=context)


def angular(request):
    return render(request, "elastic/angular.html")
