import json
import pprint

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django_rq import job

from concepts.models import Concept, Topic
from data.models import Variable
from ddionrails.setup import setup
from instruments.models import Question
from publications.models import Publication
from studies.models import Study
from workspace.models import Basket, BasketVariable

# HELPERS


def _get_object(object_type, object_id):
    object_type = object_type.title()
    if object_type in ["Variable", "Question", "Concept", "Publication"]:
        x = eval("%s.objects.get(id=%s)" % (object_type, object_id))
        return x
    else:
        return None


@job
def _rq_command():
    setup()
    print("Number of variables:", Variable.objects.count())


# VIEWS


def test_rq(request):
    # django_rq.enqueue(_rq_command)
    _rq_command.delay()
    return HttpResponse("RQ test initiated.")


def test_preview(request, object_type, object_id):
    x = _get_object(object_type, object_id)
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


def object_redirect(request, object_type, object_id):
    x = _get_object(object_type, object_id)
    if x:
        return redirect(str(x))
    else:
        return redirect("/")


def topic_list(request, study_name, language):
    study = Study.objects.get(name=study_name)
    topics = study.get_topiclist(language)
    return HttpResponse(json.dumps(topics), content_type="application/json")


def concept_by_study(request, study_name, language, concept_name):
    study = Study.objects.get(name=study_name)
    concept = Concept.objects.get(name=concept_name)
    variable_set = Variable.objects.filter(
        concept_id=concept.id, dataset__study_id=study.id
    ).distinct()
    question_set = Question.objects.filter(
        questions_variables__variable__concept_id=concept.id,
        instrument__study_id=study.id,
    ).distinct()
    if (
        request.GET.get("html", None) == "true"
        or request.GET.get("variable_html", None) == "true"
    ):
        context = dict(variables=variable_set.all(), language=language)
        return render(request, "studies/topic_variable_table.html", context=context)
    elif request.GET.get("question_html", None) == "true":
        context = dict(questions=question_set.all(), language=language)
        return render(request, "studies/topic_question_table.html", context=context)
    else:
        result = dict(
            study_id=study.id,
            study_name=study.name,
            concept_id=concept.id,
            concept_name=concept.name,
            variable_count=variable_set.count(),
        )
        if request.GET.get("variable_list", True) != "false":
            result["variable_list"] = [
                variable.to_topic_dict(language) for variable in variable_set.all()
            ]
            result["question_list"] = [
                question.to_topic_dict(language) for question in question_set.all()
            ]
        return HttpResponse(json.dumps(result), content_type="application/json")


def topic_by_study(request, study_name, language, topic_name):
    study = Study.objects.get(name=study_name)
    topic = Topic.objects.get(name=topic_name, study=study)
    topic_id_list = [topic.id for topic in Topic.get_children(topic.id)]
    topic_id_list.append(topic.id)
    variable_set = Variable.objects.filter(
        concept__topics__id__in=topic_id_list, dataset__study_id=study.id
    ).distinct()
    question_set = Question.objects.filter(
        questions_variables__variable__concept__topics__id__in=topic_id_list,
        instrument__study_id=study.id,
    ).distinct()
    if (
        request.GET.get("html", None) == "true"
        or request.GET.get("variable_html", None) == "true"
    ):
        context = dict(variables=variable_set.all(), language=language)
        return render(request, "studies/topic_variable_table.html", context=context)
    elif request.GET.get("question_html", None) == "true":
        context = dict(questions=question_set.all(), language=language)
        return render(request, "studies/topic_question_table.html", context=context)
    else:
        result = dict(
            study_id=study.id,
            study_name=study.name,
            topic_id=topic.id,
            topic_name=topic.name,
            topic_id_list=topic_id_list,
            variable_count=variable_set.count(),
        )
        if request.GET.get("variable_list", True) != "false":
            result["variable_list"] = [
                variable.to_topic_dict(language) for variable in variable_set.all()
            ]
            result["question_list"] = [
                question.to_topic_dict(language) for question in question_set.all()
            ]
        return HttpResponse(json.dumps(result), content_type="application/json")


def baskets_by_study_and_user(request, study_name, language):
    study = Study.objects.get(name=study_name)
    baskets = Basket.objects.filter(user_id=request.user.id, study_id=study.id).all()
    result = dict(
        user_logged_in=bool(request.user.id),
        baskets=[basket.to_dict() for basket in baskets],
    )
    return HttpResponse(json.dumps(result), content_type="application/json")


def add_variables_by_concept(request, study_name, language, concept_name, basket_id):
    concept = Concept.objects.get(name=concept_name)
    variable_set = Variable.objects.filter(concept_id=concept.id)
    for variable in variable_set:
        try:
            relation, status = BasketVariable.objects.get_or_create(
                basket_id=basket_id, variable_id=variable.id
            )
        except:
            pass
    return HttpResponse("DONE")


def add_variable_by_id(request, study_name, language, variable_id, basket_id):
    variable = Variable.objects.get(pk=variable_id)
    basket = Basket.objects.get(pk=basket_id)
    relation, status = BasketVariable.objects.get_or_create(
        basket_id=basket.id, variable_id=variable.id
    )
    return HttpResponse("DONE")


def add_variables_by_topic(request, study_name, language, topic_name, basket_id):
    study = Study.objects.get(name=study_name)
    topic = Topic.objects.get(name=topic_name, study=study)
    topic_id_list = [topic.id for topic in Topic.get_children(topic.id)]
    topic_id_list.append(topic.id)
    variable_set = Variable.objects.filter(concept__topics__id__in=topic_id_list)
    for variable in variable_set:
        try:
            relation, status = BasketVariable.objects.get_or_create(
                basket_id=basket_id, variable_id=variable.id
            )
        except:
            pass
    return HttpResponse("DONE")
