import json

from django.http import HttpResponse
from django.shortcuts import redirect
from django_rq import job

from concepts.models import Concept
from data.models import Variable
from ddionrails.setup import setup
from instruments.models import Question
from publications.models import Publication


@job
def rq_command():
    setup()
    print("Number of variables:", Variable.objects.count())


def test_rq(request):
    rq_command.delay()
    return HttpResponse("RQ test initiated.")


def get_test_object(object_type, object_id):
    object_type = object_type.title()
    if object_type in ["Variable", "Question", "Concept", "Publication"]:
        x = eval("%s.objects.get(id=%s)" % (object_type, object_id))
        return x
    else:
        return None


def test_preview(request, object_type, object_id):
    x = get_test_object(object_type, object_id)
    if x:
        response = dict(
            name=x.name,
            title=x.title(),
            type=object_type.lower(),
            html="<div>This is a %s with the ID %s</div>" % (object_type, object_id),
        )
        return HttpResponse(json.dumps(response), content_type="text/plain")
    else:
        return HttpResponse("No valid type.")


def test_redirect(request, object_type, object_id):
    x = get_test_object(object_type, object_id)
    if x:
        return redirect(str(x))
    else:
        return redirect("/")
