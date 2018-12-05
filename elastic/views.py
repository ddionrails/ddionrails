import re
import pprint
from django.shortcuts import render
from studies.models import Study
from .helpers import simple_search, parse_results

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
        study = Study.objects.get(name=study_name)
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
        debug_string=pprint.pformat(results, width=120),
    )
    return render(request, "elastic/search.html", context=context)

def angular(request):
    return render(request, "elastic/angular.html")
