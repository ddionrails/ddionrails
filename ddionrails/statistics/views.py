"""Views for the statistics data visualization app."""

from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from ddionrails.concepts.models import Topic
from ddionrails.data.models.variable import Variable
from ddionrails.instruments.models.question import Question
from ddionrails.studies.models import Study

NAMESPACE = "statistics"


def statistics_detail_view(
    request: HttpRequest, study: Study, plot_type: str
) -> HttpResponse:
    """Render numerical and categorical statistics views."""
    context: Dict[str, Any] = {}
    statistics_server_base_url = f"{request.get_host()}{settings.STATISTICS_SERVER_URL}"
    context["statistics_server_url"] = f"{request.scheme}://{statistics_server_base_url}"

    context["namespace"] = NAMESPACE
    context["study"] = study
    context["plot_type"] = plot_type
    context["server_metadata"] = {
        "url": context["statistics_server_url"],
        "study": study.name,
    }

    context["variable"] = Variable.objects.select_related("dataset").get(
        id=request.GET["variable"]
    )
    context["question"] = (
        (
            Question.objects.filter(questions_variables__variable=context["variable"].id)
            | Question.objects.filter(
                questions_variables__variable__target_variables__target_id=context[
                    "variable"
                ].id
            )
        )
        .order_by("-period__name")
        .first()
    )

    categories = context["variable"].category_list
    context["value_labels"] = []
    context["values"] = []
    for category in categories:
        if category["value"] < 0:
            continue
        context["values"].append(category["value"])
        context["value_labels"].append(category["label_de"])
    context["variable_metadata"] = {"variable": context["variable"].id}
    if context["values"]:
        context["variable_metadata"]["y_limits"] = {
            "min": min(context["values"]),
            "max": max(context["values"]),
        }

    return render(request, "statistics/statistics_detail.html", context=context)


class StatisticsNavView(TemplateView):
    """Render overview for all numerical and categorical statistics views."""

    template_name = "statistics/statistics_navigation.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["namespace"] = NAMESPACE

        context["api_metadata"] = {
            "url": self.request.build_absolute_uri(reverse("api:variable-list")),
            "study": context["study"].name,
        }

        statistics_variables = Variable.objects.exclude(statistics_data=None).filter(
            dataset__study=context["study"]
        )
        root_topics = Topic.objects.filter(study=context["study"], parent=None)

        context["topics"] = {
            topic.name: {"label": topic.label, "label_de": topic.label_de}
            for topic in root_topics
        }

        context["categorical_variables"] = {}
        context["numerical_variables"] = {}
        for variable in statistics_variables.filter(
            statistics_data__plot_type="categorical"
        ):
            context["categorical_variables"][
                variable.id
            ] = f"{variable.label_de}: {variable.name}"

        for variable in statistics_variables.filter(
            statistics_data__plot_type="numerical"
        ):
            context["numerical_variables"][
                variable.id
            ] = f"{variable.label_de}: {variable.name}"

        return context
