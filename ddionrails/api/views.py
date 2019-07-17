# -*- coding: utf-8 -*-

""" Views for ddionrails.api app """

import uuid
from typing import Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from ddionrails.concepts.models import Concept, Topic
from ddionrails.data.models import Variable
from ddionrails.instruments.models import Question
from ddionrails.studies.models import Study
from ddionrails.workspace.models import Basket, BasketVariable

# VIEWS


# request is a required parameter
def topic_list(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    language: str,
) -> JsonResponse:
    """ Returns a topiclist as JSON by a given study_name and language """
    study = get_object_or_404(Study, name=study_name)
    topics = study.get_topiclist(language)
    return JsonResponse(topics, safe=False)


# request is a required parameter
def concept_by_study(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    language: str,
    concept_name: str,
) -> Union[HttpResponse, JsonResponse]:
    """ Returns information about a concept and study,
        including related variables and questions

        The response can be either HTML or JSON
    """
    study = get_object_or_404(Study, name=study_name)
    concept = get_object_or_404(Concept, name=concept_name)
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
        _variables = []
        for variable in variable_set.all():
            variable.set_language(language)
            _variables.append(variable)
        context = dict(variables=_variables, language=language)
        return render(request, "studies/topic_variable_table.html", context=context)
    elif request.GET.get("question_html", None) == "true":
        _questions = []
        for question in question_set.all():
            question.set_language(language)
            _questions.append(question)
        context = dict(questions=_questions, language=language)
        return render(request, "studies/topic_question_table.html", context=context)
    else:
        result = dict(
            study_id=str(study.id),
            study_name=study.name,
            concept_id=str(concept.id),
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
        return JsonResponse(result)


# request is a required parameter
def topic_by_study(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    language: str,
    topic_name: str,
) -> Union[HttpResponse, JsonResponse]:
    """ Returns information about a topic and study,
        including related variables and questions

        The response can be either HTML or JSON
    """
    study = get_object_or_404(Study, name=study_name)
    topic = get_object_or_404(Topic, name=topic_name, study=study)
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
        _variables = []
        for variable in variable_set.all():
            variable.set_language(language)
            _variables.append(variable)
        context = dict(variables=_variables, language=language)
        return render(request, "studies/topic_variable_table.html", context=context)
    elif request.GET.get("question_html", None) == "true":
        _questions = []
        for question in question_set.all():
            question.set_language(language)
            _questions.append(question)
        context = dict(questions=_questions, language=language)
        return render(request, "studies/topic_question_table.html", context=context)
    else:
        # convert to string for json response
        topic_id_list = [str(topic_id) for topic_id in topic_id_list]
        result = dict(
            study_id=str(study.id),
            study_name=study.name,
            topic_id=str(topic.id),
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
        return JsonResponse(result)


# request is a required parameter
def baskets_by_study_and_user(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    language: str,  # TODO: language is not used
) -> JsonResponse:
    """ Returns a list of the baskets for the currently logged in user """
    study = get_object_or_404(Study, name=study_name)
    baskets = Basket.objects.filter(user_id=request.user.id, study_id=study.id).all()
    result = dict(
        user_logged_in=bool(request.user.id),
        baskets=[basket.to_dict() for basket in baskets],
    )
    return JsonResponse(result)


# request is a required parameter
def add_variables_by_concept(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    language: str,  # TODO: language is not used
    concept_name: str,
    basket_id: int,
) -> HttpResponse:
    """ Add variables to a basket based on a concept_name """

    # make sure everything is found in the database
    concept = get_object_or_404(Concept, name=concept_name)
    _ = get_object_or_404(Basket, pk=basket_id)
    variable_set = Variable.objects.filter(concept_id=concept.id)
    for variable in variable_set:
        try:
            BasketVariable.objects.get_or_create(
                basket_id=basket_id, variable_id=variable.id
            )
        except:
            pass
    return HttpResponse("DONE")


# request is a required parameter
def add_variable_by_id(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,  # TODO: study_name is not used
    language: str,  # TODO: language is not used
    variable_id: uuid.UUID,
    basket_id: int,
) -> HttpResponse:
    """ Add a variable to a basket """

    # make sure everything is found in the database
    _ = get_object_or_404(Variable, pk=variable_id)
    _ = get_object_or_404(Basket, pk=basket_id)
    BasketVariable.objects.get_or_create(basket_id=basket_id, variable_id=variable_id)
    return HttpResponse("DONE")


# request is a required parameter
def add_variables_by_topic(
    request: WSGIRequest,  # pylint: disable=unused-argument
    study_name: str,
    language: str,  # TODO: language is not used
    topic_name: str,
    basket_id: int,
) -> HttpResponse:  # pylint: disable=unused-argument
    """ Add variables to a basket based on a topic_name """

    # make sure everything is found in the database
    study = get_object_or_404(Study, name=study_name)
    topic = get_object_or_404(Topic, name=topic_name, study=study)
    _ = get_object_or_404(Basket, pk=basket_id)
    topic_id_list = [topic.id for topic in Topic.get_children(topic.id)]
    topic_id_list.append(topic.id)
    variable_set = Variable.objects.filter(concept__topics__id__in=topic_id_list)
    for variable in variable_set:
        try:
            BasketVariable.objects.get_or_create(
                basket_id=basket_id, variable_id=variable.id
            )
        except:
            pass
    return HttpResponse("DONE")
